# Podman CLI Cheat Sheet

## Containers

```bash
podman run --rm <image> <cmd>                       # run a one-shot container
podman run -d --name <name> <image>                 # run in background with a stable name
podman ps -a                                        # list containers (including stopped)
podman logs <name>                                  # show container logs
podman exec -it <name> sh                           # run a shell in a running container
podman stop <name>                                  # stop a running container
podman rm -f <name>                                  # force remove container
```

## Images

```bash
podman pull <image>                                 # download an image
podman build -t localhost/<name>:<tag> .             # build from Containerfile in current dir
podman tag localhost/<name>:<tag> <registry>/<ns>/<name>:<tag>  # add another name
podman push <registry>/<ns>/<name>:<tag>             # upload to a registry
podman image history <image>                         # show layer history
podman images                                       # list local images
podman inspect <image-or-container>                 # show JSON metadata
podman rmi <image>                                   # remove an image from local storage

# Cleanup
podman image prune          # remove unused images (frees disk)
podman system prune         # remove unused objects (be careful)
podman builder prune        # remove build cache (if supported)
```

## Port Publishing

```bash
podman run -d -p 8080:80 <image>                  # all interfaces
podman run -d -p 127.0.0.1:8080:80 <image>        # loopback only
podman run -d -p 8080:80 -p 8443:443 <image>      # multiple ports
podman run -d -p 5053:53/udp <image>              # UDP port
podman run -d -p 80 <image>                       # random host port
podman port <name>                                # show active port mappings
podman inspect <name> --format '{{json .NetworkSettings.Ports}}'  # show raw port mapping JSON
```

## Networks

```bash
# Create / list / inspect / remove
podman network create <net>                                 # create a user-defined network
podman network create --internal <net>                          # no outbound access
podman network create --subnet 172.28.0.0/24 --gateway 172.28.0.1 <net>  # create a network
podman network ls                                          # list networks
podman network inspect <net>                               # show network details
podman network rm <net>                                    # remove the network

# Connect / disconnect a running container
podman network connect <net> <name>                         # attach an existing container
podman network disconnect <net> <name>                      # detach an existing container

# Which networks is a container on?
podman inspect <name> --format '{{json .NetworkSettings.Networks}}'  # show network attachments

# Container IP per network
podman inspect <name> --format '{{range $n,$v := .NetworkSettings.Networks}}{{$n}}: {{$v.IPAddress}}{{"\n"}}{{end}}'  # inspect container/image metadata

# Which containers are on a network?
podman network inspect <net> --format '{{range $id,$c := .Containers}}{{$c.Name}} {{end}}'  # list container names

# Check DNS state of a network
podman network inspect <net> --format '{{.DNSEnabled}}'      # true if container name DNS works

# Live DNS lookup from a debug container
podman run --rm --network <net> docker.io/library/alpine:latest sh -lc 'getent hosts <target>'  # run a container

# All container IPs (quick overview)
podman ps -q | xargs -I{} podman inspect {} --format '{{.Name}}: {{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}'  # list containers
```

## Volumes

```bash
podman volume create <vol>  # create a volume
podman volume ls  # list volumes
podman volume inspect <vol>  # inspect a volume
```

## Pods

```bash
podman pod create --name <pod> -p 8080:80  # create a pod
podman pod ps  # list pods
podman pod rm -f <pod>                               # stop and remove pod + containers
```

## Secrets

```bash
podman secret create <name> -  # create a secret
podman secret ls  # list secrets
podman run --secret <name> <image>  # run a container
```
