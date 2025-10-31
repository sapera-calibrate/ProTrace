# Security Policy

## Overview

ProTRACE is committed to ensuring the security of our smart contracts and systems. We take security vulnerabilities seriously and appreciate the efforts of security researchers who help us maintain the highest standards.

## Supported Versions

Currently supported versions of ProTRACE:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in ProTRACE, please follow these steps:

### 1. Contact Us

Report security vulnerabilities through one of the following channels:

- **Email**: security@protrace.io (preferred)
- **GitHub Security Advisory**: [Create a private security advisory](https://github.com/ProTRACE/ProTRACE/security/advisories/new)

### 2. Include in Your Report

Please include the following information in your report:

- **Type of vulnerability** (e.g., buffer overflow, injection, authentication bypass)
- **Full paths of affected source files**
- **Location of the affected source code** (tag/branch/commit or direct URL)
- **Step-by-step instructions to reproduce the issue**
- **Proof-of-concept or exploit code** (if possible)
- **Impact of the issue**, including how an attacker might exploit it

### 3. Response Timeline

- **Initial Response**: Within 48 hours of report submission
- **Status Update**: Weekly updates on the progress
- **Fix Timeline**: Critical issues within 7 days, high severity within 14 days
- **Public Disclosure**: After fix deployment and verification (coordinated disclosure)

## Bug Bounty Program

### Scope

The following components are in scope for bug bounties:

- **Solana Smart Contract** (`programs/protrace/`)
  - Program ID: `7cjcAJv1fgJdwVSrabX9yVXCgyK1gKVnRUBFs1ZcG2sG` (Devnet)
  - Critical vulnerabilities: Authority bypass, fund theft, state corruption
  - High vulnerabilities: DOS attacks, unauthorized state changes
  
- **DNA Extraction Module** (Rust/Python)
  - Hash collision vulnerabilities
  - Algorithm manipulation
  
- **Merkle Tree Implementation**
  - Proof forgery
  - Root manipulation

### Rewards

Bug bounties are paid at our discretion after verifying the vulnerability:

| Severity | Reward Range | Criteria |
|----------|--------------|----------|
| **Critical** | $5,000 - $10,000 | Direct theft of funds, authority bypass, complete system compromise |
| **High** | $2,000 - $5,000 | Unauthorized state changes, DOS attacks, major logic flaws |
| **Medium** | $500 - $2,000 | Minor logic flaws, edge cases, information disclosure |
| **Low** | $100 - $500 | Best practice violations, optimization issues |

**Note**: Maximum bounty is capped at 10% of value at risk, up to $10,000.

### Eligibility

To be eligible for a bounty:

1. ✅ **First Reporter**: You must be the first to report the vulnerability
2. ✅ **Responsible Disclosure**: Details have not been shared with third parties
3. ✅ **No Exploitation**: The vulnerability has not been exploited
4. ✅ **Valid Impact**: The vulnerability must have demonstrable impact
5. ✅ **Good Faith**: You must comply with our disclosure timeline

### Out of Scope

The following are **NOT** eligible for bounties:

- ❌ Issues in third-party dependencies (report to original authors)
- ❌ Theoretical vulnerabilities without proof of concept
- ❌ Social engineering attacks
- ❌ Denial of service attacks on infrastructure (not smart contract)
- ❌ Issues already known or being fixed
- ❌ Clickjacking, CSV injection, cookie issues
- ❌ Software version disclosure
- ❌ Best practices without security impact

## Disclosure Policy

### Coordinated Disclosure

We follow coordinated disclosure practices:

1. **Report**: Security researcher reports vulnerability privately
2. **Acknowledge**: We acknowledge receipt within 48 hours
3. **Validate**: We validate and assess the vulnerability
4. **Fix**: We develop and test a fix
5. **Deploy**: We deploy the fix to production
6. **Verify**: We verify the fix with the reporter
7. **Disclose**: We publicly disclose after 90 days or fix deployment (whichever comes first)

### Public Disclosure Timeline

- **Critical/High**: 7-14 days after fix deployment
- **Medium/Low**: 30 days after fix deployment
- **Coordinated**: We work with researchers on disclosure timing

## Security Best Practices

When interacting with ProTRACE:

### For Users

- ✅ Always verify Program IDs before interacting
- ✅ Use official frontends only
- ✅ Check transaction details before signing
- ✅ Never share private keys or seed phrases
- ✅ Verify Merkle proofs independently

### For Developers

- ✅ Follow Solana security best practices
- ✅ Use latest stable versions of dependencies
- ✅ Implement proper access controls
- ✅ Validate all inputs
- ✅ Test edge cases thoroughly
- ✅ Audit code before mainnet deployment

## Security Audits

### Completed Audits

- 🔄 **Pending**: Initial audit scheduled

### Ongoing Security Measures

- ✅ **Code Reviews**: All changes reviewed by multiple developers
- ✅ **Automated Testing**: Comprehensive test suite with CI/CD
- ✅ **Monitoring**: 24/7 monitoring of on-chain activity
- ✅ **Upgrades**: Controlled upgrade process with timelock
- ✅ **Incident Response**: Dedicated security team on standby

## Contact Information

### Security Team

- **Email**: security@protrace.io
- **GitHub**: https://github.com/ProTRACE/ProTRACE/security
- **Response Time**: 24-48 hours

### Emergency Contacts

For critical, time-sensitive issues:

- **Emergency Email**: emergency@protrace.io
- **Response Time**: < 12 hours

## Acknowledgments

We thank the following security researchers for responsibly disclosing vulnerabilities:

- *Currently empty - be the first!*

## Legal

By participating in our bug bounty program, you agree to:

1. Not exploit the vulnerability beyond proof-of-concept
2. Not publicly disclose the vulnerability until coordinated
3. Comply with all applicable laws and regulations
4. Allow ProTRACE to use your name in acknowledgments (optional)

## Updates

This security policy is subject to change. Last updated: October 31, 2025

---

**Remember**: Security is everyone's responsibility. If you see something, say something!

For general questions about ProTRACE security: hello@protrace.io
