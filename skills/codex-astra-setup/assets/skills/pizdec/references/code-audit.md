# Complete Code Audit Profile

Apply to every discovered project, script collection, infrastructure tree, plugin, skill, or automation package.

## Understand the system before finding bugs

For each project, determine:

- Purpose, owners implied by configuration, languages/frameworks, entrypoints, processes, background jobs, routes, commands, event handlers, and deployment units.
- Trust boundaries, user and service identities, roles, tenants, sessions, secrets, data stores, queues, files, third-party APIs, privileged operations, and irreversible actions.
- How frontend, backend, worker, database, infrastructure, CI/CD, bot, and agent components connect in deployed reality.

## Review by selected depth

After the breadth inventory, review critical paths first: entrypoints, exposed routes and services, authentication, authorization, privileged operations, secrets, deployments, agent tools, externally triggered jobs, and irreversible actions.

- In `TRIAGE`, apply this deep review to the one or two projects selected by the coverage profile. Inspect any additional project only when the priority pass exposes a more dangerous root or cross-project trust path.
- In `FULL`, apply it to every active, deployed, exposed, privileged, or security-connected project. Read all security-relevant files and trace every material trust boundary; record any sampling of lower-risk supporting files.
- In `TOTAL`, read every first-party and unknown-copied file after the priority pass. Include source, hidden configuration, infrastructure, migrations, templates, scripts, hooks, tests, examples, generated configuration sources, documentation that changes agent behavior, and local patches.

Do not infer risk only from a directory name such as `scripts`, `tools`, `examples`, or `tests`. Follow the mode-specific contract in `coverage.md`.

## Trace sources to consequences

Identify untrusted input from HTTP, WebSocket, RPC, GraphQL, CLI, files, archives, environment, databases, queues, webhooks, bots, emails, browser content, prompts, retrieved documents, repository text, and third-party responses.

Trace it through parsing, normalization, validation, authentication, authorization, business rules, persistence, rendering, queries, file paths, outbound requests, command execution, dynamic loading, code generation, and agent tools. A dangerous function is a finding only when reachability and controls are understood; the absence of a keyword match is not evidence of safety.

## Mandatory vulnerability families

Review every applicable family:

- Authentication, registration, invitation, password reset, MFA, sessions, tokens, cookies, logout, recovery, account linking, and credential rotation.
- Authorization, ownership, roles, tenant isolation, IDOR/BOLA, mass assignment, hidden fields, admin boundaries, and confused-deputy paths.
- SQL, NoSQL, ORM raw queries, shell/command, template, expression, LDAP, XPath, header, log, email, and formula injection.
- XSS, HTML/Markdown rendering, CSS/URL injection, CSP bypass, open redirect, clickjacking, CSRF, CORS, and browser storage.
- Path traversal, unsafe uploads/downloads, archive extraction, symlinks, temporary files, MIME confusion, image/document processing, and public storage.
- SSRF, DNS rebinding, unsafe URL fetches, proxy abuse, request smuggling/splitting, XML/XXE, unsafe deserialization, prototype pollution, dynamic import, `eval`-like behavior, and generated code.
- Memory/resource exhaustion, regex denial of service, unbounded pagination/queues/uploads, rate-limit gaps, race conditions, replay, idempotency, double spending, and TOCTOU.
- Cryptography, randomness, signature verification, key handling, password hashing, TLS validation, insecure fallbacks, and custom security algorithms.
- Error handling, debug output, logs, analytics, backups, exports, source maps, PII, financial data, and secret disclosure.
- Business-logic abuse, price/quantity manipulation, workflow skipping, state-transition errors, refund/credit abuse, and destructive operations.
- Prompt injection, tool injection, unsafe memory, arbitrary tool arguments, browser/computer control, data exfiltration, and excessive agency.

## Language and framework behavior

Account for framework defaults, middleware order, route inheritance, dependency injection, serialization rules, ORM behavior, template escaping, build-time environment substitution, client/server boundaries, and production flags. Review effective configuration and deployment state instead of assuming framework defaults are active.

## Frontend and client code

Assume all shipped client code and configuration are public. Identify embedded secrets, privileged API credentials, direct database access, hidden admin operations, source maps, environment substitution, insecure storage, trust in client-side authorization, unsafe deep links, and update/signing paths.
