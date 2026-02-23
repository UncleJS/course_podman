# Module 10: `podman play kube`

`podman play kube` runs a subset of Kubernetes YAML locally.

## Learning Goals

- Understand what `play kube` can and cannot do.
- Run a pod from YAML.
- Use YAML as a repeatable definition of a local stack.
- Know how to tear it down cleanly.

## Lab: Run a Pod from YAML

Use the example file:

- `examples/kube/webpod.yaml`

Commands:

```bash
podman play kube examples/kube/webpod.yaml      # create resources from YAML
podman ps                                       # list containers
curl -sS http://127.0.0.1:8080/ | head          # verify nginx responds
podman kube down examples/kube/webpod.yaml      # tear down resources created by play kube
```

Inspect created resources:

```bash
podman ps -a --pod  # list containers
podman pod ps  # list pods
```

Common gotcha:

- resources created by play kube are named based on YAML metadata
- use `podman kube down <yaml>` to clean up consistently

## Production Note

You can also run Kube YAML under systemd using a Quadlet `.kube` unit. This can be useful for "YAML-defined" services without a full cluster.

Optional lab:

- copy `examples/quadlet/webpod.kube` and `examples/quadlet/webpod.yaml` into `~/.config/containers/systemd/`
- reload systemd and start `webpod.service`
- verify `http://127.0.0.1:8084/`

Commands:

```bash
mkdir -p ~/.config/containers/systemd  # create directory
cp examples/quadlet/webpod.kube ~/.config/containers/systemd/  # copy file
cp examples/quadlet/webpod.yaml ~/.config/containers/systemd/  # copy file
systemctl --user daemon-reload                  # regenerate units from Quadlet files
systemctl --user start webpod.service           # start the YAML-defined pod
curl -sS http://127.0.0.1:8084/ | head          # verify nginx responds
systemctl --user stop webpod.service            # stop the service
```

## Secrets Note

Kubernetes YAML secrets often appear as base64-encoded strings.

- Base64 is not encryption.
- Do not treat YAML `Secret` objects as safe to commit unless you are using an encryption workflow (see the external secrets survey).

If you need repeatable dev secrets:

- keep secret material out of YAML
- provision secrets out-of-band (Podman secret, systemd creds, SOPS)

## Limitations To Know

`podman play kube` is not full Kubernetes.

Examples of things that may differ or be unsupported:

- Services/Ingress behavior
- advanced controllers (Deployments, StatefulSets)
- cluster-level storage APIs

Treat it as a local runner for a subset of YAML.

## Checkpoint

- You can run and stop a YAML-defined pod.
- You understand the security implications of YAML-stored secrets.

## Quick Quiz

1) Why is base64 not a secret storage mechanism?

2) What is the safest teardown command for resources created by `play kube`?

## Further Reading

- `podman-play-kube(1)`: https://docs.podman.io/en/latest/markdown/podman-play-kube.1.html
- `podman-kube-down(1)`: https://docs.podman.io/en/latest/markdown/podman-kube-down.1.html
- Kubernetes objects overview: https://kubernetes.io/docs/concepts/overview/working-with-objects/kubernetes-objects/
- Kubernetes Secrets (base64 caveat): https://kubernetes.io/docs/concepts/configuration/secret/
