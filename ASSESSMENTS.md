# Assessments

These assessments focus on practical skills.

## Module Checkpoints

Each module ends with a checkpoint. Treat it as "must be able to do without notes".

## Practical Exam A (Mid-Course)

Scenario:

- You are given a container that exits immediately.

Requirements:

- Determine why it exits.
- Fix it without rebuilding the image.
- Provide a short runbook: commands used, what you observed, final fix.

Rubric:

- Uses `podman ps -a`, `podman logs`, `podman inspect` effectively.
- Fix is minimal and reproducible.
- No secrets printed.

## Practical Exam B (Final)

Scenario:

- You are given a two-service stack: web + db.
- The stack must survive reboot.

Requirements:

- Use Quadlet (systemd user service) to run both services.
- Use a named volume for state.
- Use a secret mounted as a file (not env vars).
- DB is private; only web is published.
- Provide backup + restore steps.

Rubric:

- Rootless and reboot-safe (linger configured if required).
- Correct storage and networking.
- Secrets handled safely.
- Clear, testable runbook.
