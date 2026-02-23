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
podman build -t localhost/<name>:<tag> .
podman tag localhost/<name>:<tag> <registry>/<ns>/<name>:<tag>
podman push <registry>/<ns>/<name>:<tag>
podman image history <image>
podman images
podman inspect <image-or-container>
podman rmi <image>

# Cleanup
podman image prune
podman system prune
podman builder prune
```

## Port Publishing

```bash
podman run -d -p 8080:80 <image>                  # all interfaces
podman run -d -p 127.0.0.1:8080:80 <image>        # loopback only
podman run -d -p 8080:80 -p 8443:443 <image>      # multiple ports
podman run -d -p 5053:53/udp <image>              # UDP port
podman run -d -p 80 <image>                       # random host port
podman port <name>                                 # show active mappings
podman inspect <name> --format '{{json .NetworkSettings.Ports}}'
```

## Networks

```bash
# Create / list / inspect / remove
podman network create <net>
podman network create --internal <net>                          # no outbound access
podman network create --subnet 172.28.0.0/24 --gateway 172.28.0.1 <net>
podman network ls
podman network inspect <net>
podman network rm <net>

# Connect / disconnect a running container
podman network connect <net> <name>
podman network disconnect <net> <name>

# Which networks is a container on?
podman inspect <name> --format '{{json .NetworkSettings.Networks}}'

# Container IP per network
podman inspect <name> \
  --format '{{range $n,$v := .NetworkSettings.Networks}}{{$n}}: {{$v.IPAddress}}{{"\n"}}{{end}}'

# Which containers are on a network?
podman network inspect <net> --format '{{range $id,$c := .Containers}}{{$c.Name}} {{end}}'

# Check DNS state of a network
podman network inspect <net> --format '{{.DNSEnabled}}'

# Live DNS lookup from a debug container
podman run --rm --network <net> docker.io/library/alpine:latest \
  sh -lc 'getent hosts <target>'

# All container IPs (quick overview)
podman ps -q | xargs -I{} podman inspect {} \
  --format '{{.Name}}: {{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}'
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
