const port = Number(process.env.PORT ?? "3000");
const url = `http://127.0.0.1:${port}/healthz`;

try {
  const res = await fetch(url);
  process.exit(res.ok ? 0 : 1);
} catch {
  process.exit(1);
}
