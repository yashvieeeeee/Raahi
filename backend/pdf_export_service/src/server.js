/**
 * Express server for one-click Raahi PDF exports.
 */

import cors from "cors";
import express from "express";

import { APP_ORIGINS, PATHS, SERVICE_PORT } from "./config.js";
import exportRoutes from "./routes/exportRoutes.js";

const app = express();

app.use(express.json());
app.use(cors({
  origin(origin, callback) {
    if (!origin || APP_ORIGINS.includes(origin)) {
      callback(null, true);
      return;
    }
    callback(new Error(`Origin not allowed: ${origin}`));
  }
}));

app.get("/health", (_request, response) => {
  response.json({
    status: "ok",
    service: "raahi-pdf-export-service",
    database: PATHS.database,
    metrics: PATHS.metrics
  });
});

app.use("/api", exportRoutes);

app.use((error, _request, response, _next) => {
  console.error(error);
  response.status(500).json({
    error: error.message || "PDF generation failed."
  });
});

app.listen(SERVICE_PORT, () => {
  console.log(`Raahi PDF export service listening on http://127.0.0.1:${SERVICE_PORT}`);
});
