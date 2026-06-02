import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import react from "@vitejs/plugin-react";
import { createServer } from "vite";


const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
process.chdir(root);

const server = await createServer({
  configFile: false,
  root,
  base: "/tech-cards/",
  plugins: [react()],
  server: {
    port: 3000,
    open: true,
    proxy: {
      "/techcard": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false,
      },
      "/res": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});

await server.listen();
server.printUrls();
