import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

import react from "@vitejs/plugin-react";
import { build } from "vite";


const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
process.chdir(root);

await build({
  configFile: false,
  root,
  base: "/tech-cards/",
  plugins: [react()],
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});
