# Module 4: Secrets (Local-First)

This module replaces the common beginner pattern of putting passwords in `.env` files and environment variables.

## Learning Goals

- Explain why environment variables are not a good secret transport.
- Create and use Podman secrets in rootless mode.
- Mount secrets as files and consume them safely.
- Rotate a secret with minimal downtime.
- Build a "no-secrets-in-logs" habit.

## Mental Model

- A secret is a named blob managed by Podman.
- At runtime, Podman mounts that secret into the container as a file (default: `/run/secrets/<name>`).
- Your app reads the file.

What this helps with:

- Avoids accidental leaks via `env`, process listings, or committing `.env`.
- Keeps secret material out of image layers.

What this does NOT magically solve:

- Distribution of secrets across many hosts.
- Automatic rotation.
- Encryption-at-rest unless you add it externally.

Threat model in one line:

- Podman secrets help with accidental exposure; they do not turn a laptop into a secret manager.

## Common Anti-Patterns

- `export DB_PASSWORD=...` in your shell
- putting passwords in `.env` and committing it
- `podman run -e DB_PASSWORD=...` for anything beyond a throwaway lab
- logging connection strings that contain credentials

## Commands

Create/list/inspect/remove:

```bash
podman secret create db_password -
podman secret ls
podman secret inspect db_password
podman secret rm db_password
```

Create a secret from a file:

```bash
chmod 600 ./db_password.txt
podman secret create db_password ./db_password.txt
```

Use a secret at runtime:

```bash
podman run --rm --secret db_password \
  docker.io/library/busybox:latest \
  sh -lc 'test -f /run/secrets/db_password && echo "secret file present"'
```

You can change the target filename inside the container:

```bash
podman run --rm --secret db_password,target=db.pass \
  docker.io/library/busybox:latest \
  sh -lc 'test -f /run/secrets/db.pass && echo OK'
```

Notes:

- Keep the secret value out of your shell history. Prefer `read -s` or a file with tight permissions.
- Do not print secret contents in logs.

## Lab A: Create and Mount a Secret

## Lab A: Create and Mount a Secret

1) Create a secret from stdin (example only):

```bash
printf '%s' 'correct-horse-battery-staple' | podman secret create db_password -
```

2) Run a container that confirms the secret file exists (without printing it):

```bash
podman run --rm --secret db_password docker.io/library/busybox:latest \
  sh -lc 'test -f /run/secrets/db_password && echo OK'
```

3) Verify you are not relying on environment variables:

```bash
podman run --rm --secret db_password docker.io/library/busybox:latest \
  sh -lc 'env | wc -l'
```

Checkpoint:

- Secret appears as a file at `/run/secrets/db_password`.
- You never printed the secret value.

## Lab A2: Prove It Is Not an Env Var

This lab builds the "prove it" habit.

1) Start a long-lived container with the secret:

```bash
podman run -d --name secret-demo --secret db_password docker.io/library/busybox:latest sleep 600
```

2) Check environment does not contain the secret:

```bash
podman exec secret-demo sh -lc 'env | grep -i password || true'
```

3) Confirm the file exists:

```bash
podman exec secret-demo sh -lc 'ls -la /run/secrets'
```

4) Cleanup:

```bash
podman rm -f secret-demo
```

## Lab B: Rotation Pattern (Versioned Secrets)

Use versioned names and switch consumers:

```bash
printf '%s' 'v1-value' | podman secret create db_password_v1 -
printf '%s' 'v2-value' | podman secret create db_password_v2 -
```

Run with v1, then update to v2:

```bash
podman run --rm --secret db_password_v1 docker.io/library/busybox:latest \
  sh -lc 'test -f /run/secrets/db_password_v1 && echo running-v1'

podman run --rm --secret db_password_v2 docker.io/library/busybox:latest \
  sh -lc 'test -f /run/secrets/db_password_v2 && echo running-v2'
```

Guideline:

- Keep the old secret around until the new deployment is verified.
- Remove old secrets only after rollback is no longer needed.

Rotation note:

- Many apps only read secrets on startup. Rotation often means "deploy a new container".

## Advanced: Build-Time Secrets (Optional)

Goal: authenticate to a private resource during image build without leaking tokens into image layers.

Because Podman/Buildah feature support varies by version, first check your toolchain:

```bash
podman build --help | sed -n '1,120p'
```

If your Podman supports build secrets, prefer:

- Passing a secret to the build command
- Using a secret mount during a build step

Key rule: never use `ARG`/`ENV` for secret material.

If you cannot use build secrets on your version:

- do not work around it by embedding secrets
- fetch private dependencies in CI and copy artifacts into the build context instead

## Common Failure Modes

- Your app expects a string env var but you mounted a file.
- File permissions/ownership do not match what the app runs as.
- You accidentally log the secret during debugging.

## Checkpoint

- You can create and mount a secret without leaking it.
- You can describe a rotation plan that includes rollback.

## Further Reading

- `podman-secret(1)`: https://docs.podman.io/en/latest/markdown/podman-secret.1.html
- OWASP Secrets Management Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html
- systemd credentials (service-provisioned files): https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#Credentials
- Kubernetes Secrets (base64 caveat context): https://kubernetes.io/docs/concepts/configuration/secret/
