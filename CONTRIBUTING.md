# Contributing to [App Name]

## Privacy-First Development

Before adding any feature:

1. Does it require collecting new personal data?
2. If yes, is it in our `PRIVACY_POLICY.md`?
3. If no, add it to the policy before coding.

Never collect data "just in case" it might be useful later.

## Testing Privacy

Every feature must include tests for:

- **Access control:** User A cannot see User B's data
- **Sharing:** Revoked users lose access immediately
- **Data retention:** Old data is deleted per policy

Example:

```typescript
test("User cannot view list shared by another user", async () => {
  const userA = await signup("alice@example.com");
  const userB = await signup("bob@example.com");

  const list = await userA.createList("Groceries");
  // Revoke Bob's access
  await userA.revokeShare(list.id, userB.id);

  // Bob cannot read the list
  const result = await userB.getList(list.id);
  expect(result).toBeNull();
});
```

## Security Practices

    Never commit API keys, passwords, or secrets
    Use environment variables for all config
    Run npm audit before committing
    Update dependencies monthly

## Questions?

Open an issue:
[https://github.com/AquaticAlpaca/kitchen-manager/issues](https://github.com/AquaticAlpaca/kitchen-manager/issues)
