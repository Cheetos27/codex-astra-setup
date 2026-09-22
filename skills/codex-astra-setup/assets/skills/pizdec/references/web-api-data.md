# Web, API, Bot, and Data-Service Profile

Apply to browser frontends, mobile clients, APIs, RPC, webhooks, bots, databases, caches, queues, storage, and third-party integrations.

## Web and API surface

- Enumerate all routes, methods, versions, hosts, subdomains, virtual hosts, WebSocket/RPC/GraphQL operations, documentation, health/metrics, admin, debug, upload, export, callback, and internal endpoints.
- Map authentication, authorization, ownership, roles, tenant boundaries, rate limits, request-size limits, timeouts, errors, caching, and audit logs per route class.
- Inspect proxy trust, forwarded headers, host validation, TLS termination, HSTS, cookies, CSRF, CORS, CSP, source maps, debug mode, directory listing, default files, and sensitive response headers.
- Trace each webhook and callback through signature verification, canonicalization, timestamps, replay protection, sender identity, retries, idempotency, and consequential actions.

## Databases and data services

- Discover relational and NoSQL databases, caches, queues, search engines, object storage, analytics stores, local database files, replicas, backups, exports, and admin consoles.
- Determine bind addresses, firewall and proxy path, authentication, TLS, default/anonymous accounts, roles, least privilege, schema ownership, row-level security, tenant isolation, dangerous extensions, and public endpoints.
- Trace application credentials to their actual database privileges. Client-side or broadly shared privileged credentials are high priority.
- Review every query construction path, raw query, stored procedure, migration, search expression, cache key, queue payload, serialization boundary, and bulk import/export.
- Inspect backup encryption, retention, access, restore paths, dumps, snapshots, logs, temporary exports, deleted-data handling, and production data copied to development.

## Files and object storage

- Review bucket/container policies, signed URLs, object ownership, predictable keys, listing, overwrites, content types, browser execution, CDN caching, lifecycle, multipart upload, and public access.
- Trace uploaded data through scanners, parsers, converters, thumbnails, archives, document renderers, AI ingestion, and later downloads. Treat parsers as code-execution boundaries.

## Bots and messaging

- Verify sender identity, chat or guild allowlists, group behavior, callback signatures, command authorization, admin commands, file handling, webhook secrets, replay, forwarded-message trust, and permission changes.
- Follow each admitted account through available commands, agent tools, service identity, administrative delegation, container control, secrets, and host privilege. State explicitly whether each admitted account is effectively a host or business administrator.

## Third-party integrations

- Review OAuth scopes, API-key privilege, webhook direction, redirect URIs, token storage, refresh behavior, account linking, sandbox/production separation, retries, fail-open behavior, and what happens if the third party is compromised.
