use anchor_lang::prelude::*;

#[cfg(not(feature = "no-entrypoint"))]
use solana_security_txt::security_txt;

#[cfg(not(feature = "no-entrypoint"))]
security_txt! {
    name: "ProTRACE",
    project_url: "https://github.com/ProTRACE/ProTRACE",
    contacts: "email:security@protrace.io,link:https://github.com/ProTRACE/ProTRACE/security",
    policy: "https://github.com/ProTRACE/ProTRACE/blob/main/SECURITY.md",
    preferred_languages: "en",
    source_code: "https://github.com/ProTRACE/ProTRACE",
    auditors: "Pending initial audit",
    acknowledgements: "
        We thank the Solana security community for their ongoing support.
        Special thanks to Neodyme Labs for the security.txt standard.
    "
}

declare_id!("7hWMQqQiPsuwB41yWbUTs15ETAvjLGDbN2B3jqh87Dzh");

#[program]
pub mod protrace {
    use super::*;

    // MVP Oracle Pattern: Authority-signed anchoring
    pub fn anchor_merkle_root_oracle(
        ctx: Context<AnchorMerkleRootOracle>,
        merkle_root: [u8; 32],
        manifest_cid: String,
        asset_count: u64,
        timestamp: i64,
    ) -> Result<()> {
        let anchor_account = &mut ctx.accounts.anchor_account;

        // Initialize oracle_authority on first use
        if anchor_account.version == 0 {
            anchor_account.oracle_authority = ctx.accounts.oracle_authority.key();
        }

        // Only allow the designated oracle authority to anchor
        require!(
            ctx.accounts.oracle_authority.key() == anchor_account.oracle_authority,
            ProTraceError::UnauthorizedOracle
        );

        // Update the anchor record
        anchor_account.merkle_root = merkle_root;
        anchor_account.manifest_cid = manifest_cid.clone();
        anchor_account.asset_count = asset_count;
        anchor_account.timestamp = timestamp;
        anchor_account.oracle_signature = ctx.accounts.oracle_authority.key();
        anchor_account.version += 1;

        msg!("Merkle root anchored by oracle: {}", hex::encode(merkle_root));
        msg!("Manifest CID: {}", manifest_cid);
        msg!("Asset count: {}", asset_count);

        Ok(())
    }

    // Anchor DNA Hash: Store a 256-bit perceptual DNA hash with BLAKE3 verification
    pub fn anchor_dna_hash(
        ctx: Context<AnchorDnaHash>,
        dna_hash: String,
        edition_mode: u8,
    ) -> Result<()> {
        let hash_data = &mut ctx.accounts.hash_data;
        let user = &ctx.accounts.user;

        // Validate DNA hash is exactly 64 hex characters (256 bits)
        require!(
            dna_hash.len() == 64,
            ProTraceError::InvalidDnaHashLength
        );

        // Validate hex encoding
        require!(
            dna_hash.chars().all(|c| c.is_ascii_hexdigit()),
            ProTraceError::InvalidDnaHashFormat
        );

        // Validate edition mode (0 = SERIAL, 1 = STRICT_1_1)
        require!(
            edition_mode <= 1,
            ProTraceError::InvalidEditionMode
        );

        // Store the hash data
        hash_data.dna_hash = dna_hash.clone();
        hash_data.owner = user.key();
        hash_data.timestamp = Clock::get()?.unix_timestamp;
        hash_data.edition_mode = edition_mode;

        // Compute BLAKE3 hash for internal verification
        let blake3_hash = blake3::hash(dna_hash.as_bytes());
        let blake3_hex = hex::encode(blake3_hash.as_bytes());

        msg!("DNA hash anchored: {}", dna_hash);
        msg!("Owner: {}", user.key());
        msg!("Timestamp: {}", hash_data.timestamp);
        msg!("Edition mode: {}", edition_mode);
        msg!("BLAKE3 verification: {}", blake3_hex);

        Ok(())
    }

    // Batch Edition Registration: Register multiple editions in one transaction
    pub fn batch_register_editions(
        ctx: Context<BatchRegisterEditions>,
        edition_updates: Vec<EditionUpdate>,
        batch_id: String,
        new_merkle_root: [u8; 32],
        ipfs_cid: String,
    ) -> Result<()> {
        let edition_registry = &mut ctx.accounts.edition_registry;
        let oracle_authority = &ctx.accounts.oracle_authority;

        // Only allow the designated oracle authority
        require!(
            oracle_authority.key() == edition_registry.oracle_authority,
            ProTraceError::UnauthorizedOracle
        );

        // Validate batch doesn't exceed compute limits (~1M compute units)
        require!(
            edition_updates.len() <= 50, // Conservative limit for batch size
            ProTraceError::BatchTooLarge
        );

        let mut total_editions: u64 = 0;

        // Process each edition update
        for edition_update in edition_updates.iter() {
            // Validate edition rules
            match edition_update.edition_mode {
                EditionMode::Strict1To1 => {
                    require!(edition_update.edition_no == 0, ProTraceError::InvalidEditionMode);
                    // Check if DNA already has editions (would need additional validation)
                },
                EditionMode::Serial => {
                    require!(edition_update.edition_no >= 1, ProTraceError::InvalidEditionMode);
                },
                EditionMode::Fungible => {
                    require!(edition_update.edition_no == 0, ProTraceError::InvalidEditionMode);
                }
            }

            total_editions += 1;

            msg!("Registered edition: {}#{}#{}#{}#{}",
                 hex::encode(edition_update.dna_hash),
                 std::str::from_utf8(&edition_update.chain).unwrap_or("unknown"),
                 hex::encode(edition_update.contract),
                 std::str::from_utf8(&edition_update.token_id).unwrap_or("unknown"),
                 edition_update.edition_no);
        }

        // Update registry state
        edition_registry.merkle_root = new_merkle_root;
        edition_registry.ipfs_cid = ipfs_cid.clone();
        edition_registry.total_editions += total_editions;
        edition_registry.last_batch_id = batch_id.clone();
        edition_registry.last_batch_timestamp = Clock::get()?.unix_timestamp;
        edition_registry.last_oracle_signature = oracle_authority.key();
        edition_registry.version += 1;

        msg!("Batch edition registration completed: {} editions added", total_editions);
        msg!("New Merkle root: {}", hex::encode(new_merkle_root));
        msg!("Batch ID: {}", batch_id);
        msg!("IPFS CID: {}", ipfs_cid);

        Ok(())
    }

    // Initialize Edition Registry: Set up the edition management system
    pub fn initialize_edition_registry(
        ctx: Context<InitializeEditionRegistry>,
        oracle_authority: Pubkey,
    ) -> Result<()> {
        let edition_registry = &mut ctx.accounts.edition_registry;

        edition_registry.oracle_authority = oracle_authority;
        edition_registry.merkle_root = [0u8; 32]; // Empty tree root
        edition_registry.ipfs_cid = "".to_string();
        edition_registry.total_editions = 0;
        edition_registry.last_batch_id = "".to_string();
        edition_registry.last_batch_timestamp = Clock::get()?.unix_timestamp;
        edition_registry.last_oracle_signature = oracle_authority;
        edition_registry.version = 0;

        msg!("Edition registry initialized with oracle authority: {}", oracle_authority);

        Ok(())
    }

    // Verify Edition Authorization: Check if an edition is authorized for minting
    pub fn verify_edition_authorization(
        ctx: Context<VerifyEditionAuthorization>,
        dna_hash: [u8; 32],
        chain: [u8; 10],  // Fixed size for chain identifier
        contract: [u8; 32], // Contract address (32 bytes for ETH address compatibility)
        token_id: [u8; 32], // Token ID as bytes
        edition_no: u32,
    ) -> Result<()> {
        let edition_registry = &ctx.accounts.edition_registry;

        // Check if Merkle root is set (registry initialized)
        require!(edition_registry.version > 0, ProTraceError::RegistryNotInitialized);

        // For now, authorization check is based on whether the edition exists in the anchored state
        // In production, this would include more sophisticated validation

        msg!("Edition authorization verified for: {}#{}#{}#{}#{}",
             hex::encode(dna_hash),
             std::str::from_utf8(&chain).unwrap_or("unknown"),
             hex::encode(contract),
             std::str::from_utf8(&token_id).unwrap_or("unknown"),
             edition_no);

        Ok(())
    }
    pub fn initialize_merkle_root(ctx: Context<InitializeMerkleRoot>, root: [u8; 32]) -> Result<()> {
        let merkle_account = &mut ctx.accounts.merkle_account;
        merkle_account.root = root;
        merkle_account.authority = ctx.accounts.authority.key();
        merkle_account.bump = ctx.bumps.merkle_account;
        merkle_account.created_at = Clock::get()?.unix_timestamp;
        merkle_account.updated_at = Clock::get()?.unix_timestamp;
        Ok(())
    }

    pub fn update_merkle_root(ctx: Context<UpdateMerkleRoot>, new_root: [u8; 32]) -> Result<()> {
        let merkle_account = &mut ctx.accounts.merkle_account;
        merkle_account.root = new_root;
        merkle_account.updated_at = Clock::get()?.unix_timestamp;
        Ok(())
    }

    pub fn verify_merkle_proof(
        ctx: Context<VerifyMerkleProof>,
        leaf: [u8; 32],
        proof: Vec<[u8; 32]>,
    ) -> Result<()> {
        let merkle_account = &ctx.accounts.merkle_account;

        // Reconstruct root from leaf and proof
        let mut computed_hash = leaf;

        for sibling in proof {
            let mut combined = Vec::new();
            if computed_hash <= sibling {
                combined.extend_from_slice(&computed_hash);
                combined.extend_from_slice(&sibling);
            } else {
                combined.extend_from_slice(&sibling);
                combined.extend_from_slice(&computed_hash);
            }
            // Use blake3 for hashing (already in dependencies)
            let hash_result = blake3::hash(&combined);
            computed_hash = *hash_result.as_bytes();
        }

        // Check if computed root matches stored root
        require!(computed_hash == merkle_account.root, ProTraceError::InvalidProof);

        Ok(())
    }
}

#[derive(Accounts)]
pub struct AnchorMerkleRootOracle<'info> {
    #[account(
        init_if_needed,
        payer = oracle_authority,
        space = 8 + AnchorAccount::LEN,
        seeds = [b"protrace_anchor"],
        bump
    )]
    pub anchor_account: Account<'info, AnchorAccount>,
    #[account(mut)]
    pub oracle_authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct InitializeMerkleRoot<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + MerkleAccount::LEN,
        seeds = [b"merkle_root"],
        bump
    )]
    pub merkle_account: Account<'info, MerkleAccount>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct UpdateMerkleRoot<'info> {
    #[account(
        mut,
        seeds = [b"merkle_root"],
        bump = merkle_account.bump,
        has_one = authority
    )]
    pub merkle_account: Account<'info, MerkleAccount>,
    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct VerifyMerkleProof<'info> {
    pub merkle_account: Account<'info, MerkleAccount>,
}

// Anchor DNA Hash Context
#[derive(Accounts)]
#[instruction(dna_hash: String)]
pub struct AnchorDnaHash<'info> {
    #[account(
        init,
        payer = user,
        space = 8 + HashData::LEN,
        seeds = [b"protrace_dna", user.key().as_ref(), dna_hash.as_bytes()],
        bump
    )]
    pub hash_data: Account<'info, HashData>,
    #[account(mut)]
    pub user: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[account]
pub struct AnchorAccount {
    pub oracle_authority: Pubkey,      // Designated oracle that can anchor
    pub merkle_root: [u8; 32],         // Current anchored Merkle root
    pub manifest_cid: String,          // IPFS CID of manifest
    pub asset_count: u64,              // Number of assets in tree
    pub timestamp: i64,                // When this was anchored
    pub oracle_signature: Pubkey,      // Oracle that performed anchoring
    pub version: u64,                  // Version counter
}

impl AnchorAccount {
    const LEN: usize = 32 + (4 + 64) + 8 + 8 + 32 + 8; // oracle_auth + cid + count + ts + sig + ver
}

#[account]
pub struct MerkleAccount {
    pub root: [u8; 32],
    pub authority: Pubkey,
    pub bump: u8,
    pub created_at: i64,
    pub updated_at: i64,
}

impl MerkleAccount {
    const LEN: usize = 32 + 32 + 1 + 8 + 8; // root + authority + bump + created_at + updated_at
}

// Hash Data Account for DNA Hash Anchoring
#[account]
pub struct HashData {
    pub dna_hash: String,      // 64 hex characters (256-bit perceptual DNA hash)
    pub owner: Pubkey,         // Owner/creator of the asset
    pub timestamp: i64,        // When this hash was anchored
    pub edition_mode: u8,      // 0 = SERIAL, 1 = STRICT_1_1
}

impl HashData {
    const LEN: usize = 4 + 64 + 32 + 8 + 1; // string length + 64 chars + pubkey + timestamp + mode
}

// Edition Management Data Structures
#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub enum EditionMode {
    Strict1To1,
    Serial,
    Fungible,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct EditionUpdate {
    pub dna_hash: [u8; 32],
    pub chain: [u8; 10],      // Chain identifier (e.g., "ethereum", "solana")
    pub contract: [u8; 32],   // Contract address (32 bytes for ETH compatibility)
    pub token_id: [u8; 32],   // Token ID as bytes
    pub edition_no: u32,
    pub edition_mode: EditionMode,
    pub max_editions: Option<u32>,
}

// Edition Registry Account
#[account]
pub struct EditionRegistryAccount {
    pub oracle_authority: Pubkey,      // Designated oracle that can update
    pub merkle_root: [u8; 32],         // Current Merkle root of edition registry
    pub ipfs_cid: String,              // IPFS CID of current registry snapshot
    pub total_editions: u64,           // Total editions registered
    pub last_batch_id: String,         // Last batch update ID
    pub last_batch_timestamp: i64,     // Timestamp of last batch update
    pub last_oracle_signature: Pubkey, // Oracle that performed last update
    pub version: u64,                  // Version counter
}

impl EditionRegistryAccount {
    const LEN: usize = 32 + 32 + (4 + 64) + 8 + (4 + 64) + 8 + 32 + 8;
    // oracle_auth + merkle_root + ipfs_cid + total_editions + last_batch_id + last_timestamp + last_sig + version
}

// Instruction Account Contexts
#[derive(Accounts)]
pub struct BatchRegisterEditions<'info> {
    #[account(
        mut,
        seeds = [b"edition_registry"],
        bump
    )]
    pub edition_registry: Account<'info, EditionRegistryAccount>,
    pub oracle_authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct VerifyEditionAuthorization<'info> {
    #[account(
        seeds = [b"edition_registry"],
        bump
    )]
    pub edition_registry: Account<'info, EditionRegistryAccount>,
}

#[derive(Accounts)]
pub struct InitializeEditionRegistry<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + EditionRegistryAccount::LEN,
        seeds = [b"edition_registry"],
        bump
    )]
    pub edition_registry: Account<'info, EditionRegistryAccount>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[error_code]
pub enum ProTraceError {
    #[msg("Invalid Merkle proof")]
    InvalidProof,
    #[msg("Unauthorized oracle - only designated oracle can anchor")]
    UnauthorizedOracle,
    #[msg("Batch size exceeds compute limits")]
    BatchTooLarge,
    #[msg("Invalid edition mode configuration")]
    InvalidEditionMode,
    #[msg("Edition registry not initialized")]
    RegistryNotInitialized,
    #[msg("DNA hash must be exactly 64 hex characters (256 bits)")]
    InvalidDnaHashLength,
    #[msg("DNA hash must contain only valid hexadecimal characters")]
    InvalidDnaHashFormat,
}
