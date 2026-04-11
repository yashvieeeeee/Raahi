/**
 * Reusable Puppeteer PDF generation helpers.
 */

import puppeteer from "puppeteer";

export const generatePdfBuffer = async (html) => {
  let browser;

  try {
    browser = await puppeteer.launch({
      headless: true,
      args: ["--no-sandbox", "--disable-setuid-sandbox"]
    });

    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: "networkidle0" });
    await page.emulateMediaType("screen");

    return await page.pdf({
      format: "A4",
      printBackground: true,
      margin: {
        top: "18px",
        right: "18px",
        bottom: "18px",
        left: "18px"
      }
    });
  } finally {
    if (browser) {
      await browser.close();
    }
  }
};
