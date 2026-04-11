/**
 * Local CLI renderer for Raahi PDF reports.
 */

import { generatePdfBuffer } from "./services/pdfService.js";
import {
  getAnalyticsReportData,
  getUsersReportData
} from "./services/reportDataService.js";
import {
  renderAnalyticsReport,
  renderUsersReport
} from "./templates/reportTemplates.js";

const reportType = process.argv[2];

const renderers = {
  analytics: async () => {
    const report = await getAnalyticsReportData();
    return renderAnalyticsReport(report);
  },
  users: async () => {
    const report = await getUsersReportData();
    return renderUsersReport(report);
  }
};

const main = async () => {
  if (!renderers[reportType]) {
    process.stderr.write(`Unsupported report type: ${reportType}\n`);
    process.exit(1);
  }

  const html = await renderers[reportType]();
  const pdfBuffer = await generatePdfBuffer(html);
  const output = Buffer.isBuffer(pdfBuffer) ? pdfBuffer : Buffer.from(pdfBuffer);
  process.stdout.write(output);
};

main().catch((error) => {
  process.stderr.write(`${error?.message || "PDF generation failed."}\n`);
  process.exit(1);
});
