# Capstone: Reboot-Safe Local Stack with Secrets, Backups, and Upgrades

<a id="table-of-contents"></a>

## Table of Contents

- [Goal](#goal)
- [Reference Stack](#reference-stack)
- [Deliverables](#deliverables)
- [Build It](#build-it)
- [First Data (Required)](#first-data-required)
- [Optional: Scheduled Backups](#optional-scheduled-backups)
- [Backup and Restore (Required)](#backup-and-restore-required)
- [Upgrade and Rollback (Required)](#upgrade-and-rollback-required)
- [Password Rotation (Required)](#password-rotation-required)
- [Notes](#notes)
- [Checkpoint](#checkpoint)
- [Quick Quiz](#quick-quiz)
- [Further Reading](#further-reading)

This capstone focuses on operational excellence, not app development.


[↑ Go to TOC](#table-of-contents)

## Goal

Run a small stack as rootless systemd user services (Quadlet-first) that:

- survives reboot
- keeps state in volumes
- uses secrets as files (not env vars)
- has a backup + restore flow
- has an upgrade + rollback flow (digest-pinned)

Success criteria:

- After a reboot, both services come back without manual intervention.
- You can produce a backup file and prove you can restore it.
- You can upgrade MariaDB/Adminer versions with a documented rollback.


[↑ Go to TOC](#table-of-contents)

## Reference Stack

- DB: MariaDB
- UI: Adminer (web DB admin)

This gives you a realistic stateful service without writing code.


[↑ Go to TOC](#table-of-contents)

## Deliverables

- Quadlet units for:
  - a private network
  - a DB container
  - a UI container
  - (optional) a backup timer/service
- A runbook:
  - first deploy
  - rotate DB password
  - take backup
  - restore from backup
  - upgrade pinned digests
  - rollback


[↑ Go to TOC](#table-of-contents)

## Build It

Use the provided example units:

- `examples/quadlet/capnet.network`
- `examples/quadlet/mariadb-data.volume`
- `examples/quadlet/cap-backups.volume`
- `examples/quadlet/cap-mariadb.container`
- `examples/quadlet/cap-adminer.container`
- `examples/quadlet/cap-backup.container` (optional)

1) Create the DB root password as a Podman secret (example only):

```bash
read -s -p 'MariaDB root password: ' P  # prompt for input
printf '\n'  # print text without trailing newline
printf '%s' "$P" | podman secret create mariadb_root_password -  # print text without trailing newline
unset P  # unset an environment variable
```

2) Install Quadlet units:

```bash
mkdir -p ~/.config/containers/systemd  # create directory
cp examples/quadlet/capnet.network ~/.config/containers/systemd/  # copy file
cp examples/quadlet/mariadb-data.volume ~/.config/containers/systemd/  # copy file
cp examples/quadlet/cap-backups.volume ~/.config/containers/systemd/  # copy file
cp examples/quadlet/cap-mariadb.container ~/.config/containers/systemd/  # copy file
cp examples/quadlet/cap-adminer.container ~/.config/containers/systemd/  # copy file
```

3) Enable linger (boot start):

```bash
sudo loginctl enable-linger "$USER"  # allow user services to start at boot
```

4) Start services:

```bash
systemctl --user daemon-reload             # regenerate units from Quadlet files
systemctl --user start cap-mariadb.service # start DB
systemctl --user start cap-adminer.service # start UI
```

5) Validate:

- Adminer responds on `http://127.0.0.1:8082/`
- DB is not published to the host

Validate DB is private:

```bash
podman port cap-mariadb || true  # show published ports
```

Expected: no published ports.


[↑ Go to TOC](#table-of-contents)

## First Data (Required)

Create a test database/table so you have something to back up:

```bash
podman run --rm --network capnet --secret mariadb_root_password docker.io/library/mariadb:11 sh -lc 'export MYSQL_PWD="$(cat /run/secrets/mariadb_root_password)"; mysql -h db -u root -e "CREATE DATABASE IF NOT EXISTS cap; CREATE TABLE IF NOT EXISTS cap.t1 (id INT PRIMARY KEY); INSERT IGNORE INTO cap.t1 VALUES (1);"'  # run a container
```


[↑ Go to TOC](#table-of-contents)

## Optional: Scheduled Backups

1) Install backup Quadlet and timer:

```bash
cp examples/quadlet/cap-backup.container ~/.config/containers/systemd/  # copy file
mkdir -p ~/.config/systemd/user  # create directory
cp examples/systemd-user/cap-backup.timer ~/.config/systemd/user/  # copy file
systemctl --user daemon-reload                 # reload new units
systemctl --user enable --now cap-backup.timer # enable scheduled backups
```

2) Trigger a backup immediately:

```bash
systemctl --user start cap-backup.service  # run a backup now
```

3) Verify backup files exist:

```bash
podman run --rm -v cap_backups:/backups docker.io/library/alpine:latest ls -la /backups  # run a container
```

Note:

- backups are stored in the `cap_backups` volume
- the backup unit runs `mysqldump` inside a container


[↑ Go to TOC](#table-of-contents)

## Backup and Restore (Required)

Backup requirements:

- backup output goes to a dedicated volume (or host path)
- backup command runs without exposing passwords in logs

Restore requirements:

- documented, tested procedure
- includes a rollback path

Restore sketch:

- start a throwaway client container on `capnet`
- feed a `.sql` file into `mysql -h db -u root`
- verify tables

### Backup (Manual)

Trigger a backup:

```bash
systemctl --user start cap-backup.service  # run a backup now
```

Find the newest backup file:

```bash
podman run --rm -v cap_backups:/backups docker.io/library/alpine:latest sh -lc 'ls -1 /backups | tail -n 5'  # run a container
```

### Restore (Manual)

Pick a backup filename from the previous step, then restore:

```bash
BACKUP_FILE=all-<timestamp>.sql
podman run --rm --network capnet -v cap_backups:/backups --secret mariadb_root_password docker.io/library/mariadb:11 sh -lc 'export MYSQL_PWD="$(cat /run/secrets/mariadb_root_password)"; mysql -h db -u root < "/backups/'"$BACKUP_FILE"'"'  # run a container
```

Verify the data is present:

```bash
podman run --rm --network capnet --secret mariadb_root_password docker.io/library/mariadb:11 sh -lc 'export MYSQL_PWD="$(cat /run/secrets/mariadb_root_password)"; mysql -h db -u root -e "SELECT * FROM cap.t1;"'  # run a container
```

Rollback idea:

- restore into a fresh volume and validate before switching (advanced)


[↑ Go to TOC](#table-of-contents)

## Upgrade and Rollback (Required)

- Record current image digests.
- Upgrade by changing digests in units and restarting.
- Roll back by restoring previous digests and restarting.

### Record Digests

Record what you are running:

```bash
podman images --digests | grep -E 'mariadb|adminer'  # list images
podman inspect cap-mariadb --format '{{.ImageName}}'  # inspect container/image metadata
podman inspect cap-adminer --format '{{.ImageName}}'  # inspect container/image metadata
```

### Pin by Digest (Recommended)

In your `.container` files, set:

- `Image=docker.io/library/mariadb@sha256:<digest>`
- `Image=docker.io/library/adminer@sha256:<digest>`

Then:

```bash
systemctl --user daemon-reload                 # regenerate units after edits
systemctl --user restart cap-mariadb.service   # restart DB
systemctl --user restart cap-adminer.service   # restart UI
```

Rollback is the same procedure with the previous digests.


[↑ Go to TOC](#table-of-contents)

## Password Rotation (Required)

Rotation plan for root password:

For this lab, choose a password without quotes or newlines to avoid shell/SQL escaping issues.

1) Create a new secret (versioned name):

```bash
read -s -p 'New MariaDB root password: ' P  # prompt for input
printf '\n'  # print text without trailing newline
printf '%s' "$P" | podman secret create mariadb_root_password_v2 -  # print text without trailing newline
unset P  # unset an environment variable
```

2) Change the password inside MariaDB while authenticated with the old one:

```bash
podman run --rm --network capnet --secret mariadb_root_password --secret mariadb_root_password_v2 docker.io/library/mariadb:11 sh -lc 'old=$(cat /run/secrets/mariadb_root_password); new=$(cat /run/secrets/mariadb_root_password_v2); export MYSQL_PWD="$old"; mysql -h db -u root -e "ALTER USER \"root\"@\"%\" IDENTIFIED BY \"${new}\"; FLUSH PRIVILEGES;"'  # run a container
```

3) Update Quadlet to reference the new secret name and restart MariaDB.

4) Verify logins with the new secret.

5) Remove the old secret only after verification:

```bash
podman secret rm mariadb_root_password  # remove old secret after verification
```


[↑ Go to TOC](#table-of-contents)

## Notes

- Password rotation often implies updating both the secret and the DB user credentials.
- Keep the old password available until the new one is verified.


[↑ Go to TOC](#table-of-contents)

## Checkpoint

- You can bring the stack up via Quadlet and it survives reboot.
- DB has no published host ports; only the UI is exposed.
- You can produce a backup file and restore it successfully.
- You can upgrade using digest pinning and roll back to a previous digest.


[↑ Go to TOC](#table-of-contents)

## Quick Quiz

1) Why is it important to test restore, not just backup?

2) What is the operational advantage of deploying by digest rather than by tag?


[↑ Go to TOC](#table-of-contents)

## Further Reading

- `podman-secret(1)`: https://docs.podman.io/en/latest/markdown/podman-secret.1.html
- Quadlet and Podman systemd integration: https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html
- MariaDB logical backup (`mysqldump`): https://mariadb.com/kb/en/mysqldump/
- Adminer project docs: https://www.adminer.org/
- systemd timers: https://www.freedesktop.org/software/systemd/man/latest/systemd.timer.html


[↑ Go to TOC](#table-of-contents)

© 2026 Jaco Steyn — Licensed under CC BY-SA 4.0 — Attribution Required
