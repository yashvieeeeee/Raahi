/**
 * Configuration for the Raahi PDF export service.
 */

import { fileURLToPath } from "url";
import { dirname, resolve } from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export const APP_ORIGINS = [
  "http://localhost:5000",
  "http://localhost:3000",
  "http://127.0.0.1:5000",
  "http://127.0.0.1:3000",
];

export const SERVICE_PORT = process.env.PDF_SERVICE_PORT || 3001;

export const PATHS = {
  database: resolve(__dirname, "../../database/models.db"),
  metrics: resolve(__dirname, "../../../raahi_ml/models/model_metrics.json"),
};
