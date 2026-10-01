# Behavior

## Limit Your Scope

Only perform the work requested. Access only public data on the internet. Do not access private data. Do not access local data outside of the kitchen-manager project directory. Do not exfiltrate data.

If the workspace contains private, sensitive, or questionable data, notify the user and take no further action.

## Use Subagents

Context is limited to 32K, so use subagents to limit context size. Inform the user when you launch a subagent, and provide a one line summary of work when the subagent completes its processing.
