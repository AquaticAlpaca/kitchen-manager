# Data Retention Policy

## User-Created Data

### Shopping Lists, Meal Plans, Pantry Inventory

- **Retention:** Indefinite (user owns this data)
- **Deletion:** User can delete anytime; purged immediately
- **Backup retention:** 30 days after user deletion (for recovery requests)

### Family Sharing Relationships

- **Retention:** Indefinite (needed for ongoing access control)
- **Deletion:** Revoke access anytime; permission purged immediately

## System Data

### Authentication Logs

- **Retention:** 90 days
- **After 90 days:** Anonymized (we know "someone" logged in, not who)
- **Purpose:** Detect unauthorized access attempts

### Analytics Events (e.g., "User created a list")

- **Retention:** 90 days
- **After 90 days:** Aggregated into reports (no individual user identifiers)
- **Purged:** After 6 months (we keep aggregate insights indefinitely)

### Database Backups

- **Retention:** Latest 7-day rolling backup + monthly archive (6 months)
- **Purpose:** Disaster recovery; encrypted with keys you control
- **After retention:** Securely destroyed

## Exceptions

### Legal Requirements

- If required by law (subpoena, court order), we'll comply and notify you unless
  legally prohibited
- We'll provide only what's legally required, not blanket data dumps

### Account Deletion

- User requests deletion → all personal data purged within 30 days
- Backups containing deleted accounts: purged after 30 days
- Aggregate analytics: user removed from all datasets

## Retention Review

We audit this policy annually. If we need to extend retention for legitimate
reasons, we'll announce changes 60 days in advance.
