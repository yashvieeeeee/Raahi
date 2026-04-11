/**
 * Configuration helpers for the Raahi PDF export service.
 */

import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const serviceRoot = path.resolve(__dirname, "..");
const projectRoot = path.resolve(serviceRoot, "..", "..");

export const SERVICE_PORT = Number(process.env.PDF_EXPORT_PORT || 3001);
export const APP_ORIGINS = (
  process.env.PDF_EXPORT_ALLOWED_ORIGINS ||
  "http://127.0.0.1:5000,http://localhost:5000,http://127.0.0.1:3000,http://localhost:3000"
)
  .split(",")
  .map((origin) => origin.trim())
  .filter(Boolean);

export const PATHS = {
  projectRoot,
  database: path.join(projectRoot, "instance", "raahi.db"),
  metrics: path.join(projectRoot, "raahi_ml", "models", "model_metrics.json")
};
