/**
 * Data loaders for analytics and user PDF reports.
 * Connects to PostgreSQL backend for real-time data access.
 */

import fs from "fs";
import pkg from "pg";
const { Client } = pkg;

import { PATHS } from "../config.js";

const DEFAULT_AQI = 85;

// PostgreSQL connection config
const DB_CONFIG = {
  host: process.env.DB_HOST || "localhost",
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || "raahi_db",
  user: process.env.DB_USER || "raahi_user",
  password: process.env.DB_PASSWORD || "raahi_password",
};

const readMetricsFile = () => {
  if (!fs.existsSync(PATHS.metrics)) {
    return {};
  }

  try {
    return JSON.parse(fs.readFileSync(PATHS.metrics, "utf-8"));
  } catch (error) {
    return {};
  }
};

const withDatabase = async (callback) => {
  const client = new Client(DB_CONFIG);
  try {
    await client.connect();
    return await callback(client);
  } finally {
    await client.end();
  }
};

const formatTimestamp = () => new Date().toLocaleString("en-IN", {
  year: "numeric",
  month: "short",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit"
});

export const getAnalyticsReportData = async () => {
  const metrics = readMetricsFile();

  return withDatabase(async (client) => {
    const usersResult = await client.query("SELECT COUNT(*) AS count FROM \"user\"");
    const totalUsers = parseInt(usersResult.rows[0]?.count || 0);

    const tripsResult = await client.query("SELECT COUNT(*) AS count FROM trip");
    const tripsLogged = parseInt(tripsResult.rows[0]?.count || 0);

    const co2Result = await client.query("SELECT COALESCE(SUM(co2_saved), 0) AS total FROM \"user\"");
    const co2Saved = parseFloat(co2Result.rows[0]?.total || 0);

    return {
      title: "Raahi Report",
      generatedAt: formatTimestamp(),
      analytics: {
        totalUsers,
        tripsLogged,
        co2Saved: Number(co2Saved).toFixed(1),
        aqi: DEFAULT_AQI
      },
      modelMetrics: {
        accuracy: Number(metrics.accuracy || 0).toFixed(1),
        precision: Number(metrics.precision || 0).toFixed(1),
        recall: Number(metrics.recall || 0).toFixed(1),
        f1Score: Number(metrics.f1_score || 0).toFixed(1),
        version: metrics.model_version || "1.0.0",
        trainingSamples: metrics.training_samples || 0
      }
    };
  });
};

export const getUsersReportData = async () => {
  return withDatabase(async (client) => {
    const result = await client.query(`
      SELECT
        name,
        email,
        phone,
        trips_taken,
        co2_saved,
        money_saved,
        joined_date,
        location_enabled,
        is_admin
      FROM "user"
      ORDER BY joined_date DESC
    `);

    const users = result.rows;

    return {
      title: "Raahi Report",
      generatedAt: formatTimestamp(),
      users: users.map((user) => ({
        name: user.name || "Unknown",
        contact: user.email || user.phone || "Not provided",
        trips: user.trips_taken || 0,
        activity: user.location_enabled ? "Active" : "Limited setup",
        role: user.is_admin ? "Admin" : "User",
        co2Saved: Number(user.co2_saved || 0).toFixed(1),
        moneySaved: Number(user.money_saved || 0).toFixed(2),
        joinedDate: user.joined_date
          ? new Date(user.joined_date).toLocaleDateString("en-IN")
          : "N/A"
      }))
    };
  });
};
