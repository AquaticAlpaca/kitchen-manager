# Kitchen Manager

Track ingredients. Create meal plans. Generate shopping lists: automatically!

Want to make kitchen management easy? Update stock levels with a single click?
Set required minimums? This app makes meal prep fun again.

## Privacy and Security

See: /docs for our commitments

## Javascript Package Management

npm v12 will introduce a breaking change; install-time scripts will no longer
run automatically when packages are added or updated. This will lead to runtime
errors if a package is updated and fails to run a required install script.

To fix, keep an explicit list of packaged that are allowed to run install-time
scripts (package.json:`allowScripts`); pin these to the specific version, then
manually decide whether to reapprove at the next version change. For all other
packages, deny them (package.json:`denyScripts`) without pinning.

Add a CI gate that failes if anything is pending:

```
# fails the build if any package's scripts are unreviewed
test -z "$(npm approve-scripts --allow-scripts-pending)"
```

These steps will provide three benefits:

- Avoid runtime errors
- Avoid running untrusted scripts
- Reduce the number of errors and warnings produced by npm

See
https://indragustiprasetya.com/blog/npm-v12-breaking-changes-lock-down-install-scripts.html
for more details.

## Contribuing

Found a bug? Let us know what you expected to happen, what happened instead, and
what you tried.

Want to submit a change? If your pull request includes and passes automated
tests, it gets priority!
