# Security.txt Implementation

ProTRACE includes embedded security contact information following the [solana-security-txt](https://github.com/neodyme-labs/solana-security-txt) standard.

## Overview

The security.txt standard makes it easy for security researchers to contact project teams when they discover vulnerabilities. The contact information is embedded directly in the program binary on-chain.

## Program Security Information

Our Solana program includes the following security information:

- **Name**: ProTRACE
- **Project URL**: https://github.com/ProTRACE/ProTRACE
- **Contacts**: 
  - Email: security@protrace.io
  - Security Page: https://github.com/ProTRACE/ProTRACE/security
- **Security Policy**: https://github.com/ProTRACE/ProTRACE/blob/main/SECURITY.md
- **Source Code**: https://github.com/ProTRACE/ProTRACE
- **Preferred Languages**: English (en)
- **Auditors**: Pending initial audit
- **Acknowledgements**: Security community and Neodyme Labs

## Querying Security Information

### Install Query Tool

```bash
cargo install query-security-txt
```

### Query Deployed Program (Devnet)

```bash
# Query on-chain program
query-security-txt 7cjcAJv1fgJdwVSrabX9yVXCgyK1gKVnRUBFs1ZcG2sG --url devnet
```

### Query Local Binary

```bash
# Before deployment, verify local binary
query-security-txt target/deploy/protrace.so
```

**Expected Output:**
```
Program: ProTRACE
Project URL: https://github.com/ProTRACE/ProTRACE
Contacts: email:security@protrace.io,link:https://github.com/ProTRACE/ProTRACE/security
Policy: https://github.com/ProTRACE/ProTRACE/blob/main/SECURITY.md
Preferred Languages: en
Source Code: https://github.com/ProTRACE/ProTRACE
Auditors: Pending initial audit
Acknowledgements: 
    We thank the Solana security community for their ongoing support.
    Special thanks to Neodyme Labs for the security.txt standard.
```

## Implementation Details

### Cargo.toml

Added dependency:
```toml
[dependencies]
solana-security-txt = "1.1.1"
```

### lib.rs

Added security_txt macro with `no-entrypoint` guard:
```rust
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
```

The `#[cfg(not(feature = "no-entrypoint"))]` attribute ensures the security_txt is only included in the final program binary, not when used as a library.

## Reporting Security Issues

If you discover a security vulnerability:

1. **DO NOT** create a public GitHub issue
2. **DO** report via one of these channels:
   - Email: security@protrace.io
   - GitHub Security Advisory: [Create private advisory](https://github.com/ProTRACE/ProTRACE/security/advisories/new)

3. **Include**:
   - Vulnerability description
   - Steps to reproduce
   - Proof of concept (if applicable)
   - Potential impact

4. **Expect**:
   - Response within 48 hours
   - Weekly status updates
   - Coordinated disclosure timeline

See our full [Security Policy](../SECURITY.md) for details on our bug bounty program and disclosure process.

## Building with Security.txt

### Clean Build

```bash
cd ProRust
anchor build
```

### Verify Security Information

```bash
query-security-txt target/deploy/protrace.so
```

### Deploy to Devnet

```bash
anchor deploy --provider.cluster devnet
```

### Verify On-Chain

```bash
query-security-txt <YOUR_PROGRAM_ID> --url devnet
```

## Updating Security Information

To update security contact information:

1. Edit `programs/protrace/src/lib.rs`
2. Modify the `security_txt!` macro values
3. Rebuild: `anchor build`
4. Deploy update: `anchor upgrade`
5. Verify: `query-security-txt <PROGRAM_ID>`

**Important**: Updating security information requires a program upgrade. Consider linking to a web page for information that changes frequently.

## Best Practices

### For This Project

✅ **We include**:
- Project name and URL
- Multiple contact methods (email + security page)
- Link to detailed security policy
- Source code repository
- Acknowledgements

✅ **We maintain**:
- Detailed SECURITY.md policy
- Bug bounty program
- Coordinated disclosure process
- Regular security reviews

### For Library Authors

If using this program as a dependency, the `no-entrypoint` feature guard ensures no conflicts:

```rust
#[cfg(not(feature = "no-entrypoint"))]
security_txt! { ... }
```

This prevents "multiple definition of security_txt" linker errors.

## Resources

- **Solana Security.txt Repo**: https://github.com/neodyme-labs/solana-security-txt
- **Standard Documentation**: See repository README
- **Query Tool**: `cargo install query-security-txt`
- **ProTRACE Security Policy**: [../SECURITY.md](../SECURITY.md)

## Verification Checklist

Before mainnet deployment:

- [ ] Security.txt macro included
- [ ] All contact information current
- [ ] Security policy published and linked
- [ ] Query tool tested on local binary
- [ ] Security information verified on devnet
- [ ] Security team aware of deployment
- [ ] Monitoring systems ready

## Support

For questions about our security.txt implementation:
- Technical: hello@protrace.io
- Security: security@protrace.io
- General: See [SECURITY.md](../SECURITY.md)

---

**Last Updated**: October 31, 2025  
**Standard Version**: solana-security-txt 1.1.1
