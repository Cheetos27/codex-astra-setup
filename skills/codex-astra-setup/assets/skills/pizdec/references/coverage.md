# Coverage and Completion Gate

Use this profile for every audit. Apply only the requirements of the selected mode, and distinguish deliberate mode exclusions from unfinished required work.

## Breadth-first inventory

Discover the full authorized surface before deep review:

- Hosts, users, groups, privilege paths, interfaces, firewall, routes, listeners, services, jobs, startup, and persistence.
- Process executables, redacted command lines, service definitions, working directories, configuration sources, environment-variable names, extensions, and writable search paths.
- Containers, images, orchestrators, networks, ports, volumes, secret sources, registries, and builds.
- Git and non-Git project roots, nested repositories, service directories, web roots, deployment trees, automation folders, and mounted code.
- Manifests, locks, CI/CD, infrastructure, migrations, schemas, proxies, databases, queues, caches, storage, backups, agents, skills, plugins, MCP, and bots.
- Hidden files, symlinks, submodules, patches, hooks, history indicators, archives, backups, and binaries that affect execution.

Derive additional roots from current processes, service managers, container mounts, proxies, schedulers, shell profiles, deployments, and agent configuration. Do not rely on common directories.

## Mode contracts

### TRIAGE

Complete one bounded, high-signal pass:

- Review every discovered external or privileged listener, remote-access path, firewall boundary, management surface, published container port, and effective authentication method.
- Inspect administrative identities, direct privileged login, obvious persistence, exposed databases, dangerous mounts or sockets, public storage, secret exposure, bots, agents, MCP/tools, externally triggered automation, and CI/CD entrypoints.
- Inventory all first-party project roots. Select one or two for deeper review using, in order: public/external reachability; privilege and destructive capability; secrets and sensitive data; bot, webhook, agent, or CI triggers; active deployment or runtime; then resource use as a tie-breaker.
- In selected projects, review entrypoints, authentication, authorization, privileged operations, secrets, deployment, direct data access, query/command construction, agent tools, dependency manifests, and lifecycle hooks.
- If fewer than two projects exist, review every project. If a severe signal points to an unselected project, replace the lower-risk selection or add that project while keeping the pass bounded.

`TRIAGE` does not promise complete code coverage, inactive-project review, deep history, exhaustive dependency intelligence, or every lower-risk hardening check. Name these as deliberate mode exclusions, not accidental gaps.

### FULL

Complete a comprehensive risk-based audit:

- Review every listener and its owner, effective authentication, privilege, and exposure path.
- Complete every applicable host, network, container, data, bot, agent, CI/CD, repository, and supply-chain branch.
- Review every active, deployed, externally reachable, privileged, or security-connected first-party project.
- Read every security-relevant source, configuration, infrastructure, migration, template, script, hook, deployment, and agent-behavior file in those projects. Trace every material trust boundary and privileged or irreversible operation.
- Lower-risk supporting files may be sampled only after their role is understood and the sampling is recorded. Inactive and disconnected projects may remain inventoried-only unless they share credentials, deployment paths, runtime identities, writable privileged paths, or production data.

`FULL` does not promise every first-party file, every inactive project, all reachable Git history, runtime-only behavior, or unrestricted current-vulnerability verification. Name every deliberate exclusion.

### TOTAL

Complete the exhaustive read-only audit:

- Satisfy every `FULL` requirement.
- Understand every first-party project, including inactive projects, and review every first-party and unknown-copied file.
- Review large files in chunks and record completion; never infer an unread remainder.
- Assess vendor/generated provenance, integrity, lock state, local modifications, lifecycle hooks, executable entrypoints, and privileged integrations before excluding line-by-line review.
- Inspect security-relevant repository history and retained artifacts according to the supply-chain profile; if exhaustive history or artifact verification is unauthorized or prohibited, report the exact gap.

Only `TOTAL` can emit `COMPLETE_READ_ONLY`.

## Coverage ledger

Track at least:

| Surface | Discovered | Reviewed | State | Evidence, mode exclusion, or gap |
|---|---:|---:|---|---|
| Hosts | | | | |
| External listeners/services | | | | |
| Containers/workloads | | | | |
| First-party projects | | | | |
| First-party files | | | | |
| Databases/data services | | | | |
| CI/CD and scheduled automation | | | | |
| Agents/tools/plugins | | | | |
| Secret locations and history | | | | |

Use states `reviewed`, `partially reviewed`, `mode excluded`, `not accessible`, and `not applicable`. A severe finding does not complete unread required branches.

Maintain these passes: inventory; host/services; containers/data; projects/code; agents/supply chain; cross-boundary synthesis. Do not enter final synthesis with a required pass unfinished unless the terminal result is `PARTIAL_READ_ONLY`.

Count first-party files after classification when `FULL` or `TOTAL` requires file-level coverage. In `TRIAGE`, record a numeric project count and numeric reviewed/discovered file counts for the selected projects when practical; otherwise state `NOT_ENUMERATED_BY_MODE` rather than inventing a denominator.

Do not count `.git` internals, dependency trees, virtual environments, package caches, generated builds, compiled output, or media as first-party after confirming their role. Treat local patches and unknown copied code as first-party.

## Shard large audits

Partition by non-overlapping infrastructure surface, project root, trust boundary, component, or directory. Use one project root per worker unless tightly related projects are small enough to share a shard. Keep shared entrypoints and cross-component paths for coordinator synthesis.

For `FULL` and `TOTAL`, size a shard by usable context:

- If context capacity is known, target no more than 20% of a worker's context for source payload.
- Otherwise, target about 50,000 source characters and no more than 100 security-relevant files. File count is a fallback ceiling.
- Give a large or dense file its own shard. Split the rest by non-overlapping trust boundary, component, directory, or explicit file batch.
- Run an inventory-only shard first when counts or ownership are unknown.

Each shard records assigned scope, discovered/reviewed/excluded counts, state, gaps, and evidence-backed findings. Workers receive the same authority, redaction, no-execution, mode, and no-remediation rules. Workers never declare global completion.

Keep the authoritative ledger in the coordinating context. Reconcile duplicates, late roots, exclusions, and unfinished work. Review shared identities, credentials, proxies, queues, databases, deployment tokens, and agent tools across shard boundaries.

If delegation is unavailable, process the same shards sequentially through the runtime's native continuation mechanism. Do not require a vendor-specific user command.

## Completion statuses

Use `TRIAGE_COMPLETE` only when every `TRIAGE` requirement is complete, selected projects and selection reasons are named, integer infrastructure/project counts exist, and deliberate exclusions are explicit.

Use `FULL_COMPLETE` only when every `FULL` requirement is complete, every active or security-connected project is covered, material trust paths are traced, required reviewed/discovered counts exist, and deliberate exclusions are explicit.

Use `COMPLETE_READ_ONLY` only in `TOTAL` when:

- Every listener maps to a reviewed owner, effective authentication, privilege path, and exposure boundary or is explicitly out of scope.
- Every applicable host, container, code, web/data, and agent/supply-chain profile is complete.
- Every first-party project is understood and every first-party file is reviewed.
- Effective authentication, authorization, privilege, data, and deployment paths are known.
- No required read-only critical surface is inaccessible or merely sampled.
- Integer reviewed/discovered counts exist for listeners, containers, projects, and first-party files.

All completion statuses mean complete only within the selected authorized safe read-only contract. They never imply target code execution, exploitation, unrestricted external scanning, full vulnerability-database freshness, or absence of runtime-only defects.

If a selected mode's requirement fails, use `PARTIAL_READ_ONLY`, name every gap, and avoid claiming that no additional critical or high risks exist. Continue while safe authorized inspection or supported continuation remains.

## Terminal conditions

Use `NONE` when the selected mode completed. A terminal `PARTIAL_READ_ONLY` report may use only:

- `ACCESS_DENIED`: authorized non-interactive read-only privilege still cannot inspect the named surface.
- `USER_LIMIT_REACHED`: an explicit user time, cost, scope, or tool limit was reached.
- `RUNTIME_LIMIT_REACHED`: an observed hard context, turn, worker, execution, or availability limit remains after supported continuation is exhausted.
- `PROHIBITED_VERIFICATION`: remaining evidence requires mutation, credential guessing, exploitation, secret disclosure, or unauthorized external access.

Large file counts, elapsed time, concise findings, anticipated limits, or an already confirmed severe issue are not terminal conditions for required `FULL` or `TOTAL` work. A prohibited external check never excuses unread required local scope; an inaccessible path never excuses other accessible paths.

Before reporting, apply this state machine:

```text
required = requirements(selected_mode)
if any safely inspectable required item is unfinished:
    continue or create a follow-up shard
    if the current context must end and native resume exists: emit AUDIT_CONTINUE
    otherwise do not emit a human report
elif required coverage counts are missing or invalid:
    reconstruct the ledger; do not report
elif no required gap remains:
    report completion_status(selected_mode) with stop code NONE
elif every remaining required gap has an evidenced allowed terminal code:
    report PARTIAL_READ_ONLY with that code
else:
    continue safely without claiming completion
```

## Continuation protocol

When a context must end but required work can resume, emit this capsule instead of a human report:

```text
AUDIT_CONTINUE
Mode: <TRIAGE, FULL, or TOTAL>
Coverage: listeners <reviewed>/<discovered>; containers <reviewed>/<discovered>; projects <reviewed>/<discovered>; first-party files <reviewed>/<discovered or NOT_ENUMERATED_BY_MODE>
Selected projects: <TRIAGE project roots and reasons, or NOT_APPLICABLE>
Reconciled changes: <integer additions/removals/reclassifications and evidence; or NONE>
Completed shards: <identifiers>
Next shards: <non-overlapping identifiers and boundaries>
Confirmed findings retained: <finding IDs and severities only>
Changes: NOT_PERFORMED
```

The capsule must be the entire visible response, begin with `AUDIT_CONTINUE`, contain ledger-derived values, and contain no narrative, commands, secret values, or raw code. It is not a terminal result. On resume, reload this skill and applicable profiles, verify the capsule against native task state, and continue.

Inventory and classify a newly discovered root before handoff so no required denominator is silently unknown. Compare each capsule to its predecessor and explain every denominator change caused by discovery, deduplication, or evidenced reclassification.
