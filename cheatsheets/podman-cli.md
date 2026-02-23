# Podman CLI Cheat Sheet

## Containers

```bash
podman run --rm <image> <cmd>
podman run -d --name <name> <image>
podman ps -a
podman logs <name>
podman exec -it <name> sh
podman stop <name>
podman rm -f <name>
```

## Images

```bash
podman pull <image>
podman images
podman inspect <image-or-container>
podman rmi <image>
```

## Networks

```bash
podman network create <net>
podman network ls
```

## Volumes

```bash
podman volume create <vol>
podman volume ls
podman volume inspect <vol>
```

## Pods

```bash
podman pod create --name <pod> -p 8080:80
podman pod ps
podman pod rm -f <pod>
```

## Secrets

```bash
podman secret create <name> -
podman secret ls
podman run --secret <name> <image>
```
