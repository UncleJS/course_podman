# Module 6: Networking (Ports, DNS, User-Defined Networks)

## Learning Goals

By the end of this module you will be able to:

- Explain how rootless networking differs from rootful networking and why it matters.
- Publish container ports to the host and verify them.
- Create, inspect, and remove user-defined networks.
- Connect containers to multiple networks simultaneously.
- Use container DNS names for reliable inter-container service discovery.
- Choose the right network driver (bridge, host, none, macvlan) for a given scenario.
- Configure network-level security: isolate backends, expose only what you need.
- Troubleshoot DNS, port, routing, and firewall problems methodically.
- Connect containers across pods and across user-defined networks.
- Understand how networking interacts with Quadlet (systemd) deployments.

---

## 1  How Container Networking Works (Mental Model)

Before running commands, build the mental model. Every container gets:

1. **A network namespace** — an isolated network stack with its own interfaces, routes, and firewall rules.
2. **A virtual Ethernet pair (veth)** — one end lives inside the container, the other end connects to a virtual bridge (or the host).
3. **An IP address** assigned from the network's subnet.

When two containers are on the **same user-defined network**, the bridge lets them talk to each other by IP. Podman's embedded DNS resolver makes them also reachable **by name**.

When a container is only on the **default network** (Podman's built-in `podman` bridge), DNS-based discovery is disabled. This is a deliberate design choice — it motivates you to create explicit named networks.

### 1.1  The Four Network Drivers

| Driver | What it does | When to use it |
|--------|-------------|----------------|
| `bridge` | Virtual L2 bridge; default for user-defined networks | Almost everything |
| `host` | Container shares the host network namespace | Low-level tools, benchmarking, rootful only (rootless has caveats) |
| `none` | No network interface except loopback | Batch jobs, maximum isolation |
| `macvlan` | Container appears as a separate MAC on your LAN | IoT, legacy apps that need a real LAN address |

> **Rootless note:** `host` network mode has limited usefulness in rootless Podman because the container still cannot bind privileged ports without extra capability. `macvlan` requires root on most kernels. Stick to `bridge` unless you have a specific reason.

---

## 2  Rootless Networking In Depth

### 2.1  User-Mode Networking Helpers

In rootless mode Podman cannot create kernel-level bridges as a normal user. Instead it delegates packet forwarding to a user-space helper:

| Helper | Notes |
|--------|-------|
| **pasta** | Newer, faster, preferred on modern distros; fewer quirks with UDP/ICMP |
| **slirp4netns** | Older, still common; slower but very portable |

Check which backend your installation uses:

```bash
podman info --format '{{.Host.NetworkBackend}}'
```

Check which per-network helper is active:

```bash
podman info --format '{{.Host.Slirp4NetnsOptions}}'
podman info --format '{{.Host.PastaOptions}}'
```

You can switch the rootless backend in `~/.config/containers/containers.conf`:

```ini
[network]
default_rootless_network_cmd = "pasta"
```

### 2.2  What Rootless Networking Cannot Do (by default)

- Bind ports < 1024 without extra OS configuration.
- Create `macvlan` / `ipvlan` adapters (kernel requires `CAP_NET_ADMIN`).
- Use `host` network mode and see the real host interfaces in the traditional sense.

### 2.3  Allowing Privileged Ports for Rootless (When Needed)

Option A — lower the unprivileged port minimum (system-wide, only if you own the machine):

```bash
sudo sysctl -w net.ipv4.ip_unprivileged_port_start=80
# make permanent
echo "net.ipv4.ip_unprivileged_port_start=80" | sudo tee /etc/sysctl.d/99-lowport.conf
sudo sysctl -p /etc/sysctl.d/99-lowport.conf
```

Option B — use a high port and put a reverse proxy (nginx, Caddy) in front. Strongly preferred in production.

Option C — use `systemd` socket activation (covered in Module 11).

---

## 3  Port Publishing

### 3.1  Basic Port Mapping

Syntax: `-p <host-port>:<container-port>`

```bash
podman run -d --name web1 -p 8080:80 docker.io/library/nginx:stable
curl -sS http://127.0.0.1:8080/ | head
```

### 3.2  Bind to a Specific Host Address

By default `-p 8080:80` listens on all host interfaces (`0.0.0.0`).
To restrict to loopback only:

```bash
podman run -d --name web-lo -p 127.0.0.1:8080:80 docker.io/library/nginx:stable
```

To listen on a specific network interface IP:

```bash
podman run -d --name web-iface -p 192.168.1.100:8080:80 docker.io/library/nginx:stable
```

This is important for security: a backend service should never be published to `0.0.0.0` when it only needs to be reachable by a local proxy.

### 3.3  Multiple Port Mappings

```bash
podman run -d --name multi \
  -p 8080:80 \
  -p 8443:443 \
  docker.io/library/nginx:stable
```

### 3.4  UDP Port Mapping

```bash
podman run -d --name dns-demo \
  -p 5053:53/udp \
  -p 5053:53/tcp \
  docker.io/library/alpine:latest sleep 600
```

### 3.5  Random Host Port (Ephemeral)

```bash
podman run -d --name rand-port -p 80 docker.io/library/nginx:stable
podman port rand-port          # see what port was assigned
```

### 3.6  Inspect Published Ports

```bash
# Quick view
podman port web1

# Full JSON (useful in scripts)
podman inspect web1 --format '{{json .NetworkSettings.Ports}}'

# Everything in one JSON dump
podman inspect web1 | python3 -m json.tool | grep -A10 '"Ports"'
```

Cleanup:

```bash
podman rm -f web1 web-lo web-iface multi rand-port
```

---

## 4  The Default Network vs User-Defined Networks

### 4.1  Why the Default Network Is Not Enough

When you run `podman run` without `--network`, the container joins the default `podman` bridge.

Problems with the default network:

1. **No automatic DNS.** Containers cannot find each other by name.
2. **Shared blast radius.** All containers on the default network can reach each other at the IP level.
3. **No isolation.** A compromised container can attempt connections to any other container on the same bridge.

### 4.2  Creating a User-Defined Network

```bash
podman network create appnet
```

List networks:

```bash
podman network ls
```

Expected output includes your new `appnet` plus built-in networks.

Inspect the network (shows subnet, gateway, driver):

```bash
podman network inspect appnet
```

Key fields to understand:

```
"driver": "bridge"
"subnets": [{ "subnet": "10.89.x.0/24", "gateway": "10.89.x.1" }]
"dns_enabled": true
```

Notice `dns_enabled: true` — this is the key difference from the default network.

### 4.3  Custom Subnet and Gateway

```bash
podman network create \
  --subnet 172.28.0.0/24 \
  --gateway 172.28.0.1 \
  myapp-net
```

Use custom subnets when:
- You need deterministic IPs (rare; prefer DNS names instead).
- You need to avoid subnet collisions with your VPN or office network.

### 4.4  Internal Networks (No External Access)

An internal network has no route to the outside world. Containers on it cannot reach the internet.

```bash
podman network create --internal db-internal
```

Use this for databases, caches, and any service that has no business reaching the internet.

Verify:

```bash
podman run --rm --network db-internal docker.io/library/alpine:latest \
  sh -lc 'wget -qO- --timeout=3 http://example.com || echo BLOCKED'
```

Expected: connection times out or is refused. That is the intended behavior.

### 4.5  Remove a Network

```bash
podman network rm appnet
```

You cannot remove a network that has active containers attached. Stop and remove containers first:

```bash
podman network rm appnet           # may fail if containers are running
podman ps --filter network=appnet  # find connected containers
podman rm -f $(podman ps -q --filter network=appnet)
podman network rm appnet
```

---

## 5  Container DNS and Service Discovery

### 5.1  How It Works

Podman runs an embedded DNS resolver (backed by **aardvark-dns** on modern versions). When `dns_enabled: true` on a network:

- Every container on that network is registered with its **container name** and any **network aliases**.
- DNS queries inside containers are answered by the Podman DNS resolver.
- The resolver is reachable at the network gateway address (usually the first usable IP on the subnet).

### 5.2  Basic DNS Lab

```bash
podman network create testdns

# Start a named container
podman run -d --name server-a --network testdns docker.io/library/alpine:latest sleep 600

# From another container, resolve the name
podman run --rm --network testdns docker.io/library/alpine:latest \
  sh -lc 'getent hosts server-a'
```

Expected output: an IP address followed by `server-a`.

Test TCP connectivity:

```bash
podman run --rm --network testdns docker.io/library/alpine:latest \
  sh -lc 'nc -zv server-a 80 2>&1 || echo "port not open (expected if alpine)"'
```

### 5.3  Network Aliases

An alias lets you give a container an **additional DNS name** on a specific network. This is useful for:

- Running multiple containers that all answer as `db` (blue/green rotation).
- Giving a container a short service name regardless of its actual container name.

```bash
podman network create alias-demo

podman run -d \
  --name primary-db \
  --network alias-demo \
  --network-alias db \
  docker.io/library/alpine:latest sleep 600

# Resolve by alias
podman run --rm --network alias-demo docker.io/library/alpine:latest \
  sh -lc 'getent hosts db'
```

Both the container name (`primary-db`) and the alias (`db`) resolve to the same IP.

### 5.4  Multiple Containers Sharing an Alias (Load-Balancing Pattern)

When multiple containers share the same alias on a network, DNS returns **all IPs** (round-robin).

```bash
podman network create lb-demo

podman run -d --name app-1 --network lb-demo --network-alias app docker.io/library/alpine:latest sleep 600
podman run -d --name app-2 --network lb-demo --network-alias app docker.io/library/alpine:latest sleep 600

# Resolve - you may see both IPs
podman run --rm --network lb-demo docker.io/library/alpine:latest \
  sh -lc 'for i in 1 2 3 4; do getent hosts app; done'

# Cleanup
podman rm -f app-1 app-2
podman network rm lb-demo
```

> This is primitive load balancing. For production you want a real load balancer in front. But the DNS pattern is real.

### 5.5  Custom DNS Servers

Override the DNS server used inside a container (useful on corporate networks or when using a split-horizon DNS):

```bash
podman run --rm --dns 1.1.1.1 docker.io/library/alpine:latest \
  sh -lc 'cat /etc/resolv.conf'
```

Add DNS search domains:

```bash
podman run --rm --dns-search corp.example.com docker.io/library/alpine:latest \
  sh -lc 'cat /etc/resolv.conf'
```

Set a custom `/etc/hosts` entry:

```bash
podman run --rm --add-host myservice:10.0.1.50 docker.io/library/alpine:latest \
  sh -lc 'getent hosts myservice'
```

---

## 6  Connecting Containers to Multiple Networks

A container can be a member of more than one network simultaneously. This is the correct way to build a tiered architecture:

```
[internet] → [frontend-net] → [app] → [backend-net] → [db]
```

- `app` is on both `frontend-net` and `backend-net`.
- `db` is only on `backend-net`.
- `frontend` is only on `frontend-net`.

### 6.1  Multi-Network Example

```bash
podman network create frontend-net
podman network create backend-net

# DB: only on backend
podman run -d --name db \
  --network backend-net \
  docker.io/library/alpine:latest sleep 600

# App: on both networks
podman run -d --name app \
  --network frontend-net \
  docker.io/library/alpine:latest sleep 600

# Connect app to backend AFTER it is running
podman network connect backend-net app

# Frontend: only on frontend
podman run -d --name frontend \
  --network frontend-net \
  docker.io/library/alpine:latest sleep 600

# Verify: frontend can reach app
podman exec frontend sh -lc 'getent hosts app'

# Verify: frontend CANNOT reach db (different network)
podman exec frontend sh -lc 'getent hosts db || echo "NOT REACHABLE"'

# Verify: app CAN reach db
podman exec app sh -lc 'getent hosts db'

# Cleanup
podman rm -f db app frontend
podman network rm frontend-net backend-net
```

### 6.2  Disconnect from a Network Without Stopping

```bash
podman network disconnect backend-net app
```

Verify the container no longer has the interface:

```bash
podman exec app ip addr
```

Reconnect:

```bash
podman network connect backend-net app
```

---

## 7  Inspecting Network State

### 7.1  List All Networks

```bash
podman network ls
```

### 7.2  Detailed Network Info

```bash
podman network inspect appnet
```

Shows: driver, subnets, gateways, connected containers, DNS state.

### 7.3  Which Network Is a Container On?

```bash
podman inspect <name> --format '{{json .NetworkSettings.Networks}}'
```

Or see all networks and their connected containers:

```bash
podman network inspect appnet --format '{{json .Containers}}'
```

### 7.4  Show Container IP Address

```bash
podman inspect <name> \
  --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'
```

For multi-network containers:

```bash
podman inspect app \
  --format '{{range $name, $net := .NetworkSettings.Networks}}{{$name}}: {{$net.IPAddress}}{{"\n"}}{{end}}'
```

### 7.5  View Interfaces Inside a Running Container

```bash
podman exec <name> ip addr
podman exec <name> ip route
podman exec <name> cat /etc/resolv.conf
```

### 7.6  Host-Side View

On the host, Podman bridge networks appear as `podman` prefixed virtual bridges:

```bash
ip link show type bridge
ip addr show
```

---

## 8  Network Drivers — Deeper Look

### 8.1  Bridge (Default)

```bash
podman network create --driver bridge mybridge
```

Characteristics:
- Creates a Linux bridge on the host.
- Uses NAT (masquerade) for outbound traffic.
- Containers get private IPs; host reaches them via the bridge.

### 8.2  None (No Networking)

```bash
podman run --rm --network none docker.io/library/alpine:latest ip addr
```

Only `lo` (loopback) is present. Useful for:
- Batch jobs that need complete network isolation.
- Security-sensitive workloads that must never dial out.

### 8.3  Host (Rootful Only — with Caveats)

```bash
# Note: limited usefulness in rootless mode
podman run --rm --network host docker.io/library/alpine:latest ip addr
```

The container sees the host's network interfaces directly. There is no NAT, no port mapping needed. Avoid this in production rootless workloads.

### 8.4  macvlan (Requires Root or Capabilities)

```bash
# rootful or with NET_ADMIN capability only
podman network create \
  --driver macvlan \
  --opt parent=eth0 \
  --subnet 192.168.1.0/24 \
  --gateway 192.168.1.1 \
  macvlan-net
```

The container appears as a distinct host on your physical LAN. Useful for legacy protocols (DHCP from upstream, mDNS, etc.).

---

## 9  Network Security Patterns

### 9.1  The Principle: Expose Nothing You Don't Need To

Every port you publish is an attack surface. Every network link you create is a potential pivot point.

Default stance:

- **Databases** → no port published, internal network only.
- **Caches** → no port published, internal network only.
- **APIs** → port published to loopback or internal network, reverse proxy in front.
- **Reverse proxy** → the only container with a public port.

### 9.2  Segment Networks by Trust Zone

```
[public-net]   web / proxy containers only
[app-net]      app containers + proxy
[db-net]       db containers + app
```

The DB is never on `public-net`. The proxy is never on `db-net`.

### 9.3  Combine with `--internal` Flag

```bash
podman network create --internal private-db
podman run -d --name postgres \
  --network private-db \
  -e POSTGRES_PASSWORD=secret \
  docker.io/library/postgres:16-alpine
```

This DB can never initiate outbound connections. It cannot call home, exfiltrate data to an external server, or participate in an outbound botnet.

### 9.4  Use `--network-alias` for Service Contracts

Name your services after their role, not their implementation:

```bash
--network-alias db         # not "postgres-16-container-prod"
--network-alias cache      # not "redis-7.2"
--network-alias api        # not "my-app-v3"
```

When you upgrade a service, you swap the container and preserve the alias. Nothing else needs to change.

### 9.9  Avoid Publishing to 0.0.0.0 Unnecessarily

```bash
# Bad for an internal API
-p 8080:8080              # listens on all interfaces

# Better
-p 127.0.0.1:8080:8080   # loopback only
```

---

## 10  Full Lab: Three-Tier Isolated Stack

Build a realistic, isolated three-tier stack:

- **reverse proxy** (nginx): published to host on 8080, on `frontend-net`
- **app** (alpine with netcat): on `frontend-net` and `app-net`
- **db** (alpine simulating a database): on `app-net` only, no published port

### Step 1 — Create Networks

```bash
podman network create frontend-net
podman network create --internal app-net
```

### Step 2 — Start the "DB"

```bash
podman run -d \
  --name db \
  --network app-net \
  docker.io/library/alpine:latest \
  sh -lc 'while true; do echo "DB OK" | nc -l -p 5432; done'
```

### Step 3 — Start the "App"

```bash
podman run -d \
  --name app \
  --network app-net \
  --network-alias api \
  docker.io/library/alpine:latest \
  sleep 600
```

Connect app to the frontend network as well:

```bash
podman network connect frontend-net app
```

### Step 4 — Start the Reverse Proxy

```bash
podman run -d \
  --name proxy \
  --network frontend-net \
  -p 127.0.0.1:8080:80 \
  docker.io/library/nginx:stable
```

### Step 5 — Verify Connectivity

App can reach DB:

```bash
podman exec app sh -lc 'getent hosts db && echo DNS OK'
```

Proxy can reach app:

```bash
podman exec proxy sh -lc 'getent hosts api && echo DNS OK'
```

Proxy CANNOT reach DB (different network):

```bash
podman exec proxy sh -lc 'getent hosts db 2>&1 || echo "ISOLATED: expected"'
```

DB CANNOT reach the internet (internal network):

```bash
podman exec db sh -lc 'wget -qO- --timeout=3 http://example.com 2>&1 || echo "BLOCKED: expected"'
```

Host can reach proxy via published port:

```bash
curl -sSI http://127.0.0.1:8080/
```

### Step 6 — Cleanup

```bash
podman rm -f db app proxy
podman network rm frontend-net app-net
```

---

## 11  Connecting Containers to Pods on a Network

Pods (covered in Module 7) and user-defined networks interact naturally. You can place an entire pod on a named network:

```bash
podman network create podnet

podman pod create --name mypod --network podnet -p 8090:80

podman run -d --pod mypod --name pod-nginx docker.io/library/nginx:stable

# A container outside the pod resolves the pod by its infra container's IP
# or by any container name inside:
podman run --rm --network podnet docker.io/library/alpine:latest \
  sh -lc 'getent hosts pod-nginx'

podman pod rm -f mypod
podman network rm podnet
```

---

## 12  Networking in Quadlet (systemd) Deployments

Quadlet `.network` unit files let you declare Podman networks as systemd-managed resources. This ensures networks exist before containers start.

### 12.1  Declare a Network Unit

Create `~/.config/containers/systemd/appnet.network`:

```ini
[Unit]
Description=Application private network

[Network]
Driver=bridge
Internal=true
```

### 12.2  Reference the Network in a Container Unit

In your `.container` unit file:

```ini
[Container]
Image=docker.io/library/nginx:stable
Network=appnet.network
```

Systemd will automatically create `appnet` before starting your container and the dependency chain is managed for you.

Full Quadlet networking is covered in Module 11.

---

## 13  Troubleshooting Networking

### 13.1  Symptom: Container Cannot Reach Another Container by Name

Checklist:

1. Are both containers on the **same user-defined network**? (Not the default `podman` network.)
2. Is `dns_enabled: true` on that network?
3. Are both containers **running** (not exited)?
4. Are you using the **container name** (or an alias), not the hostname?

```bash
# Check network membership
podman inspect <name> --format '{{json .NetworkSettings.Networks}}'

# Verify DNS is enabled on the network
podman network inspect <net> --format '{{.DNSEnabled}}'

# Try a live DNS lookup from a debug container
podman run --rm --network <net> docker.io/library/alpine:latest \
  sh -lc 'getent hosts <target-name>'
```

### 13.2  Symptom: Cannot Connect Even Though DNS Resolves

DNS working but TCP failing means the service is not listening, is on the wrong port, or there is a firewall rule.

```bash
# Check if the port is open
podman run --rm --network <net> docker.io/library/alpine:latest \
  sh -lc 'nc -zv <target> <port>'

# Check what the container is actually listening on
podman exec <target> ss -tlnp
# or
podman exec <target> netstat -tlnp
```

### 13.3  Symptom: Port Published But Cannot Reach from Host

```bash
# Confirm the port mapping
podman port <name>

# Confirm the process is listening inside the container
podman exec <name> ss -tlnp

# Check host firewall
sudo firewall-cmd --list-all   # firewalld
sudo iptables -L -n            # iptables / nftables

# Check the container's host binding
podman inspect <name> --format '{{json .NetworkSettings.Ports}}'
# Look for "HostIp" - if it's 127.0.0.1, you can only reach from localhost
```

### 13.4  Symptom: `nc` or `wget` Not Available in Container

Use a debug sidecar with networking tools:

```bash
podman run --rm --network <net> docker.io/library/nicolaka/netshoot:latest \
  curl -v http://<target>:<port>/
```

Or use a minimal alpine with a one-liner install:

```bash
podman run --rm --network <net> docker.io/library/alpine:latest \
  sh -lc 'apk add -q curl && curl -v http://<target>:<port>/'
```

### 13.5  Symptom: Container Cannot Reach the Internet

```bash
# Verify DNS
podman exec <name> sh -lc 'cat /etc/resolv.conf'

# Try pinging a well-known IP (not DNS-dependent)
podman exec <name> ping -c3 8.8.8.8

# Try DNS resolution
podman exec <name> sh -lc 'getent hosts example.com'

# Check if the network is internal
podman network inspect <net> --format '{{.Internal}}'
```

If the network is `internal: true`, outbound traffic is intentionally blocked.

If DNS fails but the IP works, the problem is your DNS resolver configuration.

### 13.6  Symptom: Sporadic Connection Failures (Rootless)

This is often a pasta/slirp4netns quirk with UDP under high load, or a port exhaustion issue.

```bash
# Check for errors in the rootless network helper
journalctl --user -u podman.socket
podman events --filter type=network
```

### 13.7  Useful Debugging One-Liners

```bash
# All running container IPs
podman ps -q | xargs -I{} podman inspect {} \
  --format '{{.Name}}: {{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}'

# All networks and their subnets
podman network ls -q | xargs -I{} podman network inspect {} \
  --format '{{.Name}}: {{range .Subnets}}{{.Subnet}}{{end}}'

# Which containers are on a given network
podman network inspect <net> --format '{{range $id, $c := .Containers}}{{$c.Name}} {{end}}'

# Container's effective DNS config
podman exec <name> cat /etc/resolv.conf
```

---

## 14  Common Patterns Reference

### Pattern A — Single Shared App Network (Simple Stack)

```bash
podman network create app
podman run -d --name db    --network app docker.io/library/postgres:16-alpine
podman run -d --name cache --network app docker.io/library/redis:7-alpine
podman run -d --name api   --network app -p 127.0.0.1:8000:8000 myapp:latest
podman run -d --name proxy --network app -p 0.0.0.0:80:80     nginx:stable
```

### Pattern B — Segmented Networks (Recommended for Production)

```bash
podman network create --internal data-tier
podman network create app-tier
podman network create public-tier

podman run -d --name db     --network data-tier   postgres:16-alpine
podman run -d --name cache  --network data-tier   redis:7-alpine
podman run -d --name api    --network app-tier    myapp:latest
podman network connect data-tier api              # api reaches db and cache

podman run -d --name proxy  --network public-tier -p 80:80 nginx:stable
podman network connect app-tier proxy             # proxy reaches api
```

### Pattern C — Debug Sidecar (Ephemeral)

```bash
podman run --rm -it --network <same-net> docker.io/library/alpine:latest sh
# Now you have a shell inside the network with tools
```

### Pattern D — One-Time Migration Container

```bash
podman run --rm \
  --network app-tier \
  --env-file .env \
  myapp:latest \
  ./migrate.sh
```

---

## 15  Checkpoint

You should be able to answer the following without looking at commands:

- What is the fundamental difference between the default `podman` network and a user-defined network?
- Why does `--internal` improve security for a database network?
- How do containers find each other by name (what Podman feature enables this)?
- When would you use a network alias instead of a container name?
- What flag restricts a port binding to loopback only?
- How do you connect a running container to a second network without restarting it?
- What is the first tool you reach for when a container cannot be found by DNS?

---

## 16  Quick Quiz

1. You have two containers on the default `podman` network. Container A tries to `curl http://container-b/`. It fails with "could not resolve host". What is the most likely cause and fix?

2. You start a database with `-p 5432:5432`. A security reviewer flags this as a problem. Why, and how do you fix it?

3. You have an `app` container that needs to talk to both a `frontend` network and a `backend` network. What is the cleanest way to set this up, and what command do you use to add the second network connection after the container is running?

4. Two containers share the network alias `api`. A third container queries `getent hosts api`. What does it get back? What does this enable?

5. A container can ping `8.8.8.8` but cannot resolve `example.com`. What is the most likely problem?

6. You check `podman port mycontainer` and it shows port 8080 mapped. But `curl http://127.0.0.1:8080/` fails. Name three things to check next.

---

## Further Reading

- Podman networking documentation: `man podman-network`
- aardvark-dns project (embedded DNS): https://github.com/containers/aardvark-dns
- pasta (rootless networking helper): https://passt.top/
- slirp4netns: https://github.com/rootless-containers/slirp4netns
- CNI vs Netavark: https://podman.io/blogs/2022/05/05/podman-rootful-rootless.html
- nftables and container networking: see Module 13 (Troubleshooting)
