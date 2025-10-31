use anyhow::{Context, Result};
use blake3;
use ipfs_api::IpfsClient;
use serde::{Deserialize, Serialize};
use std::fs::File;
use std::io::Read;
use std::path::PathBuf;
use structopt::StructOpt;
use hex::ToHex;
use borsh::{BorshSerialize, BorshDeserialize};

use solana_client::rpc_client::RpcClient;
use solana_sdk::signature::{read_keypair_file, Keypair, Signer};
use solana_sdk::transaction::Transaction;
use solana_sdk::instruction::{Instruction, AccountMeta};
use solana_sdk::pubkey::Pubkey;
use solana_sdk::system_program;

#[derive(StructOpt, Debug)]
#[structopt(name = "merkle-cli")]
struct Opt {
    /// path to a directory of leaf files or a single JSON file of leaves (hex)
    #[structopt(parse(from_os_str))]
    input: PathBuf,

    /// ipfs api host:port (default 127.0.0.1:5001)
    #[structopt(long, default_value = "127.0.0.1:5001")]
    ipfs: String,

    /// rpc url for anchoring on solana (e.g., https://api.devnet.solana.com)
    #[structopt(long)]
    rpc: Option<String>,

    /// anchor authority keypair file (if anchoring)
    #[structopt(long, parse(from_os_str))]
    keypair: Option<PathBuf>,

    /// program id of the deployed anchor program
    #[structopt(long)]
    program_id: Option<String>,

    /// command: build | proof | verify | upload | anchor
    #[structopt(long)]
    cmd: String,

    /// index for proof / verify (0-based)
    #[structopt(long)]
    index: Option<usize>,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
struct MerkleTreeOnIpfs {
    version: u64,
    depth: usize,
    leaf_count: usize,
    root: String, // hex
    leaves: Vec<String>, // hex leaves
    nodes: Option<Vec<String>>,
}

fn blake3_hash(data: &[u8]) -> [u8; 32] {
    let h = blake3::hash(data);
    let mut out = [0u8; 32];
    out.copy_from_slice(h.as_bytes());
    out
}

/// build tree (heap order: root at 0)
fn build_merkle_from_leaves(leaves: &Vec<[u8; 32]>) -> (Vec<[u8; 32]>, usize) {
    // pad to next power of two
    let mut n = leaves.len();
    let target = n.next_power_of_two();
    let mut padded = leaves.clone();
    let empty = blake3_hash(&[]);
    padded.resize(target, empty);

    let leaf_count = padded.len();
    let total_nodes = (leaf_count * 2) - 1;
    let mut nodes = vec![[0u8; 32]; total_nodes];
    let leaves_offset = leaf_count - 1;
    for (i, l) in padded.iter().enumerate() {
        nodes[leaves_offset + i] = *l;
    }
    for i in (0..leaves_offset).rev() {
        let left = nodes[(i * 2) + 1];
        let right = nodes[(i * 2) + 2];
        let mut input = [0u8; 64];
        input[..32].copy_from_slice(&left);
        input[32..].copy_from_slice(&right);
        nodes[i] = blake3_hash(&input);
    }
    (nodes, leaf_count)
}

/// produce proof siblings from leaf level upward
fn make_proof(nodes: &Vec<[u8;32]>, leaf_count: usize, index: usize) -> Vec<[u8;32]> {
    let mut proof = Vec::new();
    let mut pos = (leaf_count - 1) + index;
    while pos > 0 {
        let sibling = if pos % 2 == 0 { pos - 1 } else { pos + 1 };
        // if sibling is out of bound, use empty
        if sibling < nodes.len() {
            proof.push(nodes[sibling]);
        } else {
            proof.push(blake3_hash(&[]));
        }
        pos = (pos - 1) / 2;
    }
    proof
}

/// verify locally
fn verify_proof_local(leaf: [u8;32], index: usize, proof: &Vec<[u8;32]>, root: [u8;32]) -> bool {
    let mut computed = leaf;
    let mut idx = index;
    for sibling in proof.iter() {
        let mut input = [0u8; 64];
        if idx % 2 == 0 {
            input[..32].copy_from_slice(&computed);
            input[32..].copy_from_slice(&sibling);
        } else {
            input[..32].copy_from_slice(&sibling);
            input[32..].copy_from_slice(&computed);
        }
        computed = blake3_hash(&input);
        idx /= 2;
    }
    computed == root
}

// Anchor instruction args serialized with Borsh (must match on-chain signature order)
#[derive(BorshSerialize, BorshDeserialize)]
struct AnchorRootArgs {
    // same order as program: new_root: [u8;32], cid: String, version: u64
    new_root: [u8; 32],
    cid: String,
    version: u64,
}

// compute Anchor instruction discriminator: first 8 bytes of sha256("global:anchor_root")
fn anchor_instruction_discriminator(name: &str) -> [u8;8] {
    use sha2::{Digest, Sha256};
    let mut hasher = Sha256::new();
    hasher.update(format!("global:{}", name).as_bytes());
    let d = hasher.finalize();
    let mut out = [0u8;8];
    out.copy_from_slice(&d[..8]);
    out
}

#[tokio::main]
async fn main() -> Result<()> {
    let opt = Opt::from_args();

    // ipfs client
    let parts: Vec<&str> = opt.ipfs.split(':').collect();
    let ipfs = if parts.len() == 2 {
        IpfsClient::from_host_and_port(parts[0], parts[1].parse::<u16>()?)
    } else {
        IpfsClient::from_host_and_port("127.0.0.1", 5001)
    };

    match opt.cmd.as_str() {
        "build" => {
            // read input directory or json
            let mut raw_leaves_bytes: Vec<Vec<u8>> = Vec::new();
            if opt.input.is_dir() {
                for entry in std::fs::read_dir(&opt.input)? {
                    let e = entry?;
                    if e.path().is_file() {
                        let mut b = Vec::new();
                        File::open(e.path())?.read_to_end(&mut b)?;
                        raw_leaves_bytes.push(b);
                    }
                }
            } else {
                // JSON array of hex strings
                let mut s = String::new();
                File::open(&opt.input)?.read_to_string(&mut s)?;
                let arr: Vec<String> = serde_json::from_str(&s)?;
                for h in arr {
                    let bytes = hex::decode(h.trim_start_matches("0x"))?;
                    raw_leaves_bytes.push(bytes);
                }
            }

            // compute leaf hashes
            let mut leaves_hashes: Vec<[u8;32]> = Vec::new();
            for leaf in raw_leaves_bytes.iter() {
                leaves_hashes.push(blake3_hash(&leaf));
            }

            if leaves_hashes.is_empty() {
                anyhow::bail!("No leaves found");
            }

            let (nodes, leaf_count) = build_merkle_from_leaves(&leaves_hashes);
            let root = nodes[0];
            // prepare JSON to upload
            let nodes_hex: Vec<String> = nodes.iter().map(|n| hex::encode(n)).collect();
            let leaves_hex: Vec<String> = leaves_hashes.iter().map(|l| hex::encode(l)).collect();
            let manifest = MerkleTreeOnIpfs {
                version: chrono::Utc::now().timestamp() as u64,
                depth: (leaf_count as f64).log2() as usize,
                leaf_count,
                root: hex::encode(root),
                leaves: leaves_hex,
                nodes: Some(nodes_hex),
            };
            let json = serde_json::to_vec_pretty(&manifest)?;
            // save local manifest
            std::fs::write("merkle_manifest.json", &json)?;
            println!("Saved manifest -> merkle_manifest.json (root {})", hex::encode(root));

            // Upload to IPFS
            let cursor = std::io::Cursor::new(json.clone());
            let add_res = ipfs.add(cursor).await.context("ipfs add")?;
            let cid = add_res.hash;
            println!("Uploaded to IPFS CID: {}", cid);
            std::fs::write("last_cid.txt", &cid)?;
            println!("Saved last_cid.txt -> {}", cid);
        }

        "proof" => {
            let manifest_json = std::fs::read_to_string("merkle_manifest.json")?;
            let manifest: MerkleTreeOnIpfs = serde_json::from_str(&manifest_json)?;
            let idx = opt.index.context("provide --index for proof")?;
            let nodes = manifest.nodes.context("manifest must contain nodes to create proof")?;
            let nodes_bytes: Vec<[u8;32]> = nodes.iter().map(|h| {
                let bs = hex::decode(h).unwrap();
                let mut arr = [0u8;32];
                arr.copy_from_slice(&bs[..32]);
                arr
            }).collect();
            let proof = make_proof(&nodes_bytes, manifest.leaf_count, idx);
            println!("Proof ({} siblings):", proof.len());
            for p in proof.iter() {
                println!("{}", hex::encode(p));
            }
            println!("Leaf hash: {}", manifest.leaves[idx]);
            println!("Root: {}", manifest.root);
        }

        "verify" => {
            let manifest_json = std::fs::read_to_string("merkle_manifest.json")?;
            let manifest: MerkleTreeOnIpfs = serde_json::from_str(&manifest_json)?;
            let idx = opt.index.context("provide --index for verify")?;
            let nodes = manifest.nodes.context("manifest must contain nodes to verify")?;
            let nodes_bytes: Vec<[u8;32]> = nodes.iter().map(|h| {
                let bs = hex::decode(h).unwrap();
                let mut arr = [0u8;32];
                arr.copy_from_slice(&bs[..32]);
                arr
            }).collect();
            let proof = make_proof(&nodes_bytes, manifest.leaf_count, idx);
            let mut leaf = [0u8;32];
            leaf.copy_from_slice(&hex::decode(&manifest.leaves[idx])?[..32]);
            let mut root = [0u8;32];
            root.copy_from_slice(&hex::decode(&manifest.root)?[..32]);
            let ok = verify_proof_local(leaf, idx, &proof, root);
            println!("Local verify -> index {} -> {}", idx, ok);
        }

        "upload" => {
            // upload existing manifest to IPFS
            let json = std::fs::read("merkle_manifest.json")?;
            let cursor = std::io::Cursor::new(json.clone());
            let add_res = ipfs.add(cursor).await.context("ipfs add")?;
            let cid = add_res.hash;
            println!("Uploaded to IPFS CID: {}", cid);
            std::fs::write("last_cid.txt", &cid)?;
            println!("Saved last_cid.txt -> {}", cid);
        }

        "anchor" => {
            // Anchor new root + cid on-chain
            let rpc_url = opt.rpc.context("provide --rpc (e.g., https://api.devnet.solana.com)")?;
            let keypair_path = opt.keypair.context("provide --keypair path")?;
            let program_id_str = opt.program_id.context("provide --program-id of deployed program")?;
            let payer = read_keypair_file(keypair_path).context("read keypair file")?;
            let rpc = RpcClient::new(rpc_url.clone());

            // read manifest and cid
            let manifest_json = std::fs::read_to_string("merkle_manifest.json")
                .context("merkle_manifest.json must exist (build command)")?;
            let manifest: MerkleTreeOnIpfs = serde_json::from_str(&manifest_json)?;
            let cid = std::fs::read_to_string("last_cid.txt").unwrap_or_else(|_| {
                println!("Warning: last_cid.txt missing, anchor will embed empty CID. Provide CID in last_cid.txt.");
                "".to_string()
            });

            // parse program id
            let program_id: Pubkey = program_id_str.parse()?;

            // compute state PDA (seeds: ["merkle_state", authority_pubkey])
            let authority_pubkey = payer.pubkey();
            let (state_pda, _bump) = Pubkey::find_program_address(&[b"merkle_state", authority_pubkey.as_ref()], &program_id);
            println!("State PDA: {}", state_pda);

            // prepare args
            let root_bytes = hex::decode(&manifest.root)?;
            let mut root_arr = [0u8;32];
            root_arr.copy_from_slice(&root_bytes[..32]);
            let version = manifest.version;

            let args = AnchorRootArgs {
                new_root: root_arr,
                cid: cid.clone(),
                version,
            };
            let mut data = Vec::new();
            // write discriminator then args (Borsh)
            let disc = anchor_instruction_discriminator("anchor_root");
            data.extend_from_slice(&disc);
            args.serialize(&mut data).context("serialize args")?;

            // build accounts vec: state (mut), authority (signer)
            let accounts = vec![
                AccountMeta::new(state_pda, false),
                AccountMeta::new_readonly(authority_pubkey, true),
            ];

            let instruction = Instruction {
                program_id,
                accounts,
                data,
            };

            // build, sign and send tx
            let recent = rpc.get_latest_blockhash()?;
            let tx = Transaction::new_signed_with_payer(
                &[instruction],
                Some(&authority_pubkey),
                &[&payer],
                recent,
            );

            let sig = rpc.send_and_confirm_transaction(&tx)?;
            println!("Anchor tx sent. Signature: {}", sig);
            println!("Anchored root: {}", manifest.root);
            println!("CID: {}", cid);
            println!("Version: {}", version);
        }

        other => {
            println!("Unknown command: {}. supported commands: build | proof | verify | upload | anchor", other);
        }
    }

    Ok(())
}
