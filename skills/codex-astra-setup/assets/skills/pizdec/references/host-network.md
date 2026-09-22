# Host, Network, and Remote-Service Profile

Apply to every server, workstation, VM, or network-exposed runtime.

## Host baseline

- Identify OS, kernel/build, patch history, support status when locally provable, boot mode, disk encryption status, security products, firewall state, time synchronization, and update services.
- Enumerate local and directory-backed users, service accounts, administrative groups, non-interactive privilege, sudoers or equivalent policy, credential delegation, writable privileged paths, and dormant/default accounts.
- Trace administrative capability through service managers, container sockets, virtualization interfaces, mounted host paths, backup tools, device access, and remote-management software.
- Inspect permissions on keys, credentials, configuration, logs, backups, service files, executable directories, temporary directories, and search paths. Never print secret values or hashes.

## Every listener is a required audit branch

For every TCP and UDP listener, determine:

1. Bound addresses and interfaces, protocol, port, owning process or container, executable, service definition, user, working directory, and privilege.
2. Firewall and routing path, proxy or tunnel path, published container port, local/VPN/LAN/public boundary, and any existing evidence of actual reachability.
3. Effective authentication methods, authorization scope, default or dormant accounts, anonymous/guest behavior, TLS, client verification, rate limiting, brute-force protection, and audit logging.
4. Dangerous service capabilities such as file transfer, command execution, forwarding, plugins, admin panels, debug modes, APIs, and access to secrets or host control.
5. Effective configuration after defaults, includes, overrides, conditional blocks, environment, generated state, and runtime arguments.

Do not mark a port reviewed after only listing it. If owning service or effective authentication is unknown, coverage remains partial.

## SSH and similar remote shells

For every SSH service, inspect effective per-user and per-source behavior, not only explicit configuration lines:

- Password, public-key, keyboard-interactive/PAM, multi-factor, and required authentication combinations.
- Direct privileged-account login, whether the privileged password is set or locked without reading its hash, user/group allowlists, empty/default accounts, and key ownership/permissions.
- Attempt limits, connection limits, brute-force protection, firewall exposure, actual reachability evidence, logs of repeated failures, and source restrictions.
- Agent, TCP, X11, stream-local, and gateway forwarding; user environment; command restrictions; chroot or forced commands; subsystem configuration.
- Service version and patch status only when supported by current local evidence or an explicitly authorized trusted source.

Direct privileged password login on a reachable service is a high-priority finding even without an attempted login.

## Linux and Unix persistence/injectors

Inspect system and user service units, timers, cron, startup scripts, shell profiles, sudoers, polkit, SSH authorized-key options, dynamic-loader preload, library paths, interpreter startup modules, package hooks, Git hooks, writable PATH entries, capabilities, setuid/setgid files, and unexpected long-running processes. Focus on items that transform untrusted files or environment into privileged execution.

Inspect service sandboxing, including privilege dropping, filesystem isolation, private temporary space, home/system protection, capability bounding, syscall restrictions, device access, and writable executable/configuration paths.

## Windows remote access and persistence

Inspect effective Firewall profiles and rules, UAC/admin elevation, Defender or other endpoint protection, update history, disk encryption, RDP, WinRM, SMB, OpenSSH, remote registry, PowerShell remoting, remote-control products, public shares, and listening RPC services.

Inspect services, scheduled tasks, startup folders, Run keys, WMI subscriptions, shell extensions, DLL search paths, PowerShell profiles, package managers, browser native messaging, writable service executables, and auto-elevating paths. Do not execute persistence entries.

## Proxies, tunnels, and management surfaces

Inspect reverse proxies, VPNs, overlay networks, tunnels, service meshes, dashboards, orchestrator APIs, database admin tools, monitoring endpoints, metrics, tracing, debug ports, and backup consoles. Trace upstream identity and client-address trust through every proxy hop.
