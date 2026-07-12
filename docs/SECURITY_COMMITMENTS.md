# Security Commitments

## Infrastructure Security

### Supabase Hosting

- [ ] Enable encryption at rest (default in Supabase)
- [ ] Enable HTTPS only (HSTS headers)
- [ ] IP whitelisting for admin access (if applicable)
- [ ] Regular security updates (automatic with managed service)

### Database Access

- [ ] All connections use TLS 1.2+
- [ ] No plaintext passwords in code (use environment variables)
- [ ] Row-level security (RLS) enforced on every table
- [ ] Principle of least privilege (app user can't access admin functions)

## Application Security

### Authentication

- [ ] Implement rate limiting on login (prevent brute force)
- [ ] No password hints or security questions (seniors forget these)
- [ ] Passwordless option (magic links, SMS)
- [ ] Session timeout (30 minutes of inactivity for security)
- [ ] "Log out all devices" option (in case of compromise)

### Input Validation

- [ ] All user input sanitized (prevent SQL injection)
- [ ] File uploads scanned for malware (if implemented)
- [ ] No executable file uploads ever

### Data in Transit

- [ ] HTTPS only (no HTTP fallback)
- [ ] Certificate pinning for mobile app (prevent MITM attacks)
- [ ] Encrypted API keys (never stored in frontend code)

## Vulnerability Management

### Bug Bounty / Responsible Disclosure

- [ ] Public security.txt file (/.well-known/security.txt)
- [ ] Contact:
      [via Github Security and Quality](https://github.com/AquaticAlpaca/kitchen-manager/security)
- [ ] Response time: 48 hours for critical bugs
- [ ] Disclosure timeline: 90 days to fix, then public disclosure

### Security Audits

- [ ] Annual third-party security audit (recommend Cure53)
- [ ] Publish results publicly (even if embarrassing—builds trust)
- [ ] Fix critical issues within 30 days

### Dependency Updates

- [ ] Automated dependency scanning (Dependabot, Snyk)
- [ ] Update critical security patches within 7 days
- [ ] Test all updates before production deployment

## Incident Response

### Data Breach Protocol

1. Detect & contain (within 24 hours)
2. Assess impact (which users affected, what data?)
3. Notify users via email (within 72 hours per GDPR/CCPA)
4. Publish incident report (transparency > reputation management)
5. Implement preventive measures
6. Disclose findings to regulators if required

### Example Notification Email

Subject: Security Notice — We Found and Fixed a Vulnerability

Hi [User],

On [DATE], we discovered [ISSUE]. Here's what happened:

    [Impact: X users affected, Y data type]
    [What we did: Fixed the bug, audited logs, enabled monitoring]
    [What you should do: No action needed, but here's a reminder to use biometric lock]

We prioritize your privacy and security. Questions? Contact us via
[Github Issues](https://github.com/AquaticAlpaca/kitchen-manager/issues).

## What You Should Do

### Use a Strong Passphrase

- [ ] 4+ words
- [ ] Unique to this app (reused passwords are a risk)
- [ ] Or: use passwordless magic link / SMS login

### Enable Biometric Lock

- [ ] Face ID or fingerprint on your device
- [ ] We cannot unlock your account without your biometric

### Review Sharing Permissions

- [ ] Check who has access to your account
- [ ] Revoke access to inactive family members

### Update Your App

- [ ] Install updates when prompted
- [ ] We push security fixes regularly

## Transparency Reports

We will publish annual transparency reports:

- Security audits conducted and results
- Vulnerabilities discovered and patched
- Law enforcement requests (if any)
- Breach incidents (if any)

---

**Last reviewed:** 2026-07-11 **Next review:** 2027-07-11
