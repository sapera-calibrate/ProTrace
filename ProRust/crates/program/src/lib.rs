use anchor_lang::prelude::*;
use borsh::{BorshDeserialize, BorshSerialize};

declare_id!("MerkleAnchr1111111111111111111111111111111111"); // change to your program id after deploy

#[program]
pub mod merkle_anchor_program {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>, bump: u8) -> ProgramResult {
        let state = &mut ctx.accounts.state;
        state.authority = *ctx.accounts.authority.key;
        state.bump = bump;
        state.root = [0u8; 32];
        state.cid = String::from("");
        state.version = 0;
        Ok(())
    }

    pub fn anchor_root(ctx: Context<AnchorRoot>, new_root: [u8;32], cid: String, version: u64) -> ProgramResult {
        let state = &mut ctx.accounts.state;
        // version monotonic check
        require!(version > state.version, MerkleError::VersionTooOld);
        state.root = new_root;
        state.cid = cid;
        state.version = version;
        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(init, payer = authority, space = State::space(), seeds = [b"merkle_state", authority.key().as_ref()], bump)]
    pub state: Account<'info, State>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct AnchorRoot<'info> {
    #[account(mut, seeds = [b"merkle_state", state.authority.as_ref()], bump = state.bump, has_one = authority)]
    pub state: Account<'info, State>,
    pub authority: Signer<'info>,
}

#[account]
#[derive(Default)]
pub struct State {
    pub authority: Pubkey,
    pub bump: u8,
    pub root: [u8; 32], // blake3 root
    pub cid: String,    // ipfs cid for the manifest
    pub version: u64,   // monotonic
}

impl State {
    pub fn space() -> usize {
        // discriminator 8 + authority 32 + bump 1 + root 32 + cid (4 + ~200) + version 8
        8 + 32 + 1 + 32 + 4 + 200 + 8
    }
}

#[error]
pub enum MerkleError {
    #[msg("Version must be greater than the stored version.")]
    VersionTooOld,
}
