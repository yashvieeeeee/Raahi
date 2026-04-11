/**
 * Express routes for PDF report exports.
 */

import { Router } from "express";

import { generatePdfBuffer } from "../services/pdfService.js";
import {
  getAnalyticsReportData,
  getUsersReportData
} from "../services/reportDataService.js";
import {
  renderAnalyticsReport,
  renderUsersReport
} from "../templates/reportTemplates.js";

const router = Router();

const sendPdf = async (response, filename, html) => {
  const pdf = await generatePdfBuffer(html);
  const pdfBuffer = Buffer.isBuffer(pdf) ? pdf : Buffer.from(pdf);
  response.setHeader("Content-Type", "application/pdf");
  response.setHeader("Content-Disposition", `attachment; filename="${filename}"`);
  response.setHeader("Content-Length", pdfBuffer.length);
  response.end(pdfBuffer);
};

router.get("/export-analytics", async (_request, response, next) => {
  try {
    const report = await getAnalyticsReportData();
    const html = renderAnalyticsReport(report);
    await sendPdf(response, "raahi-analytics-report.pdf", html);
  } catch (error) {
    next(error);
  }
});

router.get("/export-users", async (_request, response, next) => {
  try {
    const report = await getUsersReportData();
    const html = renderUsersReport(report);
    await sendPdf(response, "raahi-users-report.pdf", html);
  } catch (error) {
    next(error);
  }
});

export default router;
