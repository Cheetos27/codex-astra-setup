# Safe Use of Local Analyzers

Use this profile for every audit. Local analyzers supplement agent reasoning; they never replace inventory, reachability analysis, effective-configuration review, or evidence validation.

## Eligibility

Use an analyzer only when it is already present in the authorized environment, its executable resolves outside the untrusted target, its local origin is reasonably established, and it can run without changing the target. Suitable categories include secret detection, static code analysis, dependency and lockfile analysis, container/image inspection, infrastructure-as-code checks, permission/configuration auditing, and locally available vulnerability intelligence.

Do not install, update, download, enable, authenticate, accept new terms for, or start an analyzer service or container. Do not invoke package installation, project builds, lifecycle scripts, target binaries, tests, or migrations to make analysis work.

Do not use a local-looking tool if it uploads code, secrets, metadata, hashes, dependency inventories, or findings to an external service unless the user explicitly authorizes that exact destination and data flow. Prefer offline operation when available.

Treat target-supplied analyzer binaries, wrappers, plugins, rules, and configuration as untrusted. Do not run a tool from the target or load executable target plugins. Use target-provided declarative rules only after confirming that they cannot execute code, expand scope, reveal secrets, or alter analyzer behavior outside the audit boundary.

## Safe execution

- Confirm the exact target paths and keep them inside the authorized scope.
- Prefer read-only or no-write options. Do not allow auto-fix, baseline generation inside the target, cache creation inside the target, configuration rewrites, or report files written into the target.
- Avoid scanning secret values into visible output. Suppress or redact matches and retain only type, minimal location, and exposure path.
- Record analyzer name, locally observed version, target, relevant mode, and vulnerability-database freshness when locally provable.
- If a tool's behavior, network use, write behavior, or target execution is unclear, skip it and state why.

## Interpret results

Treat analyzer output as leads, not verdicts. Validate each material signal against source, effective runtime configuration, reachability, authorization controls, deployment state, and exploit prerequisites before creating a finding.

Do not claim that a clean analyzer result proves safety or complete coverage. Record unavailable categories and stale or unknown databases under `What I did not verify`. Deduplicate multiple tool alerts under the same root cause.
