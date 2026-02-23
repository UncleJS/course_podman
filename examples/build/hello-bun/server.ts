const port = Number(process.env.PORT ?? "3000");

const server = Bun.serve({
  port,
  fetch(req) {
    const url = new URL(req.url);
    if (url.pathname === "/healthz") return new Response("ok\n");
    return new Response("hello from bun\n");
  },
});

console.log(`listening on 0.0.0.0:${port}`);

const shutdown = () => {
  try {
    server.stop(true);
  } catch {
    // best-effort
  }
  process.exit(0);
};

process.on("SIGTERM", shutdown);
process.on("SIGINT", shutdown);
