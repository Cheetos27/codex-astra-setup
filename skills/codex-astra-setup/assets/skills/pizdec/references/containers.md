# Containers and Orchestration Profile

Apply when any container engine, image, Dockerfile, Compose file, Kubernetes resource, registry, volume, or container network is discovered.

## Inventory and declared-versus-running state

- Enumerate engines, contexts, running and stopped workloads, images, tags/digests, registries, networks, published ports, volumes, build caches, Compose projects, Dockerfiles, and orchestration resources.
- Correlate runtime inspection with Dockerfiles, Compose, system services, environment files, deployment manifests, and proxy configuration. Report drift between declared and running state.
- Map each host listener and proxy route to its container, internal port, service identity, application project, and data stores.

## Host escape and effective privilege

Inspect:

- Privileged mode, host PID/IPC/network, host devices, added capabilities, disabled seccomp/AppArmor/SELinux, unconfined profiles, no-new-privileges, root or host UID, user namespaces, and writable root filesystems.
- Docker/container runtime sockets, orchestration credentials, hostPath/bind mounts, sensitive host directories, SSH agents, cloud credentials, service-account tokens, kernel interfaces, and nested container control.
- Membership in container-management groups and any remote API exposure. Treat writable runtime sockets as a host-administration path.
- Writable executable/configuration mounts, symlinks crossing boundaries, shared temporary directories, and secrets copied into image layers or build history.

## Network and data

- Review every published port, bind address, container firewall path, internal network, DNS, proxy route, service discovery rule, and unintended cross-project reachability.
- Inspect volume ownership, database files, backups, exports, logs, object storage, and whether deleted/replaced containers leave sensitive data accessible.
- Verify TLS and authentication on runtime APIs, registries, dashboards, databases, queues, caches, and internal services; “internal” is not equivalent to trusted.

## Image and build supply chain

- Check base-image provenance, digest pinning, mutable tags, end-of-life images when locally provable, package sources, downloaded binaries, remote ADD behavior, build secrets, multi-stage copying, ownership, entrypoints, healthchecks, and update strategy.
- Inspect lifecycle scripts and entrypoints without executing them. Trace environment and mounted input into shell expansion, templates, package installation, and generated configuration.
- Review `.dockerignore`, build context, credential leakage, source maps, debug artifacts, test keys, and copied repository history.

## Kubernetes and comparable orchestrators

Inspect RBAC, cluster-admin paths, service accounts, token automounting, secrets, admission policy, privileged workloads, host namespaces, hostPath, host ports, capabilities, security contexts, network policies, ingress, exposed dashboards, etcd, kubelet, registry credentials, and workload identity to cloud permissions.
