# External Secrets Survey (Thorough Intro, Optional Implementation)

Podman secrets are a good local-first baseline, but most teams eventually need one or more of:

- encryption-at-rest on the host
- multi-host distribution
- automated rotation
- auditing and policy

This module teaches the landscape so learners can choose an external approach confidently.

This is intentionally not a single "do this" recipe.

External secrets are an architecture and operations decision.

## What You Are Optimizing For

Use this checklist to pick a system:

- How many hosts need the secret?
- How often does it rotate?
- Who/what is allowed to read it (policy)?
- Do you need audit logs?
- What happens when the secrets system is down?
- How do you bootstrap a brand new host?

Also consider:

- do you need dynamic credentials (leases) or static secrets
- how do you revoke access
- how do you handle break-glass scenarios

## Option 1: systemd Credentials (Host-Native)

What it is:

- systemd can provision credentials to services as files.
- Credentials can be stored encrypted at rest on the host.

Why it fits this course:

- Production baseline already uses systemd user services (Quadlet-first).
- Delivery model matches the container best practice: read a file.

Typical pattern:

- Store encrypted credential material on the host.
- systemd materializes it to a runtime file.
- Container reads that file via a mount.

Operational notes:

- great for systemd-first deployments
- policy is typically "who can read files / run services" on that host
- still need a story for distributing the encrypted credential material to new hosts

When to choose it:

- Single host or small fleet.
- You want minimal moving parts.

## Option 2: SOPS (GitOps-Friendly Encrypted Files)

What it is:

- Keep secrets encrypted in git.
- Decrypt on the host/CI using an identity (age or GPG, plus cloud KMS in some setups).

Benefits:

- Change history and reviews are straightforward.
- Bootstrapping is manageable for small teams.

Tradeoffs:

- Rotation is usually a process, not a lease.
- You must secure decryption keys carefully.

Bootstrap story:

- you need a way to provision the age/GPG/KMS identity onto a new host
- you need a safe place to store recovery keys

Best-fit pattern with containers:

- Decrypt to a root-owned file with `0600`.
- Mount into the container read-only.
- Never persist decrypted files into images.

## Option 3: Vault-Class Secret Managers (Centralized)

What it is:

- Central policy + auth + audit.
- Dynamic secrets (leases) and automated rotation.

Benefits:

- Strong governance and scaling story.
- Short-lived credentials reduce blast radius.

Costs:

- Operational overhead.
- Availability becomes critical path for deploy/boot.

Common bridge patterns (recommended):

- Sidecar/agent writes a file to a shared volume; app reads the file.
- systemd service fetches secret at start, writes to a protected file, then starts the container.

Operational notes:

- design for availability: what happens on restart if Vault is unreachable
- treat auth methods (Kubernetes auth, AppRole, OIDC, etc.) as part of the threat model
- dynamic creds reduce blast radius but increase moving parts

## Comparison Table (Mental Model)

Answer these questions:

- "Do I need secrets on more than one host?"
- "Do I need automatic rotation and revocation?"
- "Do I need centralized policy and audit?"

Typical outcomes:

- single host: systemd creds or local secrets may be enough
- small fleet, GitOps: SOPS is a strong fit
- larger org/compliance: Vault-class is common

## What Does Not Change

Regardless of external system:

- The container should read secrets from files.
- Do not pass secret values in env vars, CLI args, or logs.
- Use rotation-friendly names and restart/roll strategies.

## Migration Path from Podman Secrets

If you start with Podman secrets (local-first), the clean migration is:

- external manager writes/refreshes a file
- your service consumes that file (mount) or uses systemd credentials

This avoids rewriting applications that already expect file-based secrets.

## Checkpoint

- You can explain the tradeoffs between: systemd credentials, SOPS, and Vault-class secret managers.
- You can describe a bootstrap story for a new host (how it gets the ability to decrypt/fetch).
- You can describe a file-based delivery pattern that keeps apps unchanged.

## Quick Quiz

1) In one sentence: why is base64 not encryption?

2) What question best distinguishes SOPS-style encrypted files from Vault-style leased secrets?

## Further Reading

- systemd credentials (service-provisioned files): https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#Credentials
- Mozilla SOPS: https://github.com/getsops/sops
- age (file encryption tool often used with SOPS): https://github.com/FiloSottile/age
- HashiCorp Vault: https://www.vaultproject.io/
- Kubernetes Secrets (baseline for comparison): https://kubernetes.io/docs/concepts/configuration/secret/
