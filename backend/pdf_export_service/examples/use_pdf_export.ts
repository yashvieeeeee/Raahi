/**
 * React / Next.js helper for one-click PDF downloads.
 */

export const downloadPdf = async (endpoint: string, filename: string) => {
  const response = await fetch(endpoint, {
    method: "GET",
    headers: {
      Accept: "application/pdf"
    }
  });

  if (!response.ok) {
    throw new Error(`Download failed: ${response.status}`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.URL.revokeObjectURL(url);
};

export const handleExportAnalytics = async () => {
  await downloadPdf("http://127.0.0.1:3001/api/export-analytics", "raahi-analytics-report.pdf");
};

export const handleExportUsers = async () => {
  await downloadPdf("http://127.0.0.1:3001/api/export-users", "raahi-users-report.pdf");
};
