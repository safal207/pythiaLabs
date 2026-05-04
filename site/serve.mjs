import { createServer } from "node:http";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(here, "dist");
const port = Number(process.env.PORT ?? 5173);

const mime = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".ico": "image/x-icon",
};

createServer(async (req, res) => {
  try {
    const url = decodeURIComponent((req.url ?? "/").split("?")[0]);
    let filePath = path.join(root, url);
    const safe = path.normalize(filePath);
    if (!safe.startsWith(root)) {
      res.writeHead(403).end("Forbidden");
      return;
    }
    let info;
    try {
      info = await stat(safe);
    } catch {
      res.writeHead(404).end("Not Found");
      return;
    }
    if (info.isDirectory()) {
      filePath = path.join(safe, "index.html");
    }
    const data = await readFile(filePath);
    const ext = path.extname(filePath);
    res.writeHead(200, {
      "content-type": mime[ext] ?? "application/octet-stream",
      "cache-control": "no-cache",
    });
    res.end(data);
  } catch (err) {
    res.writeHead(500).end(String(err));
  }
}).listen(port, () => {
  process.stdout.write(`serving dist/ at http://localhost:${port}\n`);
});
