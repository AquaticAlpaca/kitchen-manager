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
