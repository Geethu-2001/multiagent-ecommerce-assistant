# Security model

- Only public HTTP(S) destinations are accepted; local/private/reserved IPs and unsafe redirects are rejected.
- HTTP fetches have a timeout, response byte limit, page count limit and content-type check.
- SQL is limited to a single SELECT/CTE statement, with dangerous operations and system catalogs blocked.
- PostgreSQL statements run in read-only transactions with a statement timeout and bounded result count.
- Retrieved page/database content is passed as evidence and should never be treated as instructions by the model.
- Credentials are environment-based and should not be committed.

Important: use a dedicated PostgreSQL agent role with `CONNECT`, schema `USAGE`, and `SELECT` on approved tables only; do not grant ownership or write privileges to the agent. The compose setup separates `app_user` (schema/seed owner) from `agent_reader` (SELECT-only on tables created by `app_user`). Review grants and credentials before production use. Add network egress controls for stronger SSRF protection. Review logs and UI diagnostic output before exposing to untrusted users.
