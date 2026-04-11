/**
 * HTML templates for PDF export reports.
 */

const baseStyles = `
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500&display=swap');
    
    * { 
      box-sizing: border-box; 
      margin: 0;
      padding: 0;
    }
    
    html {
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }
    
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      color: #1f2937;
      background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
      line-height: 1.6;
    }
    
    .page {
      padding: 50px;
      max-width: 1000px;
      margin: 0 auto;
      background: white;
    }
    
    .report-shell {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 16px;
      padding: 48px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    }
    
    .header {
      border-bottom: 2px solid #f0f1f3;
      padding-bottom: 32px;
      margin-bottom: 36px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 32px;
    }
    
    .header-left h1 {
      font-size: 38px;
      font-weight: 800;
      color: #0d1117;
      letter-spacing: -0.5px;
      margin-bottom: 8px;
    }
    
    .header-left .subtitle {
      font-size: 15px;
      color: #6b7280;
      font-weight: 500;
    }
    
    .timestamp-box {
      background: linear-gradient(135deg, #f0f9ff 0%, #e0f8ff 100%);
      padding: 18px 24px;
      border-radius: 12px;
      border: 1px solid #cffafe;
      text-align: right;
      min-width: 260px;
    }
    
    .timestamp-box .label {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      color: #0369a1;
      letter-spacing: 0.5px;
      margin-bottom: 6px;
    }
    
    .timestamp-box .value {
      font-size: 14px;
      color: #0f2d4f;
      font-weight: 600;
      font-family: 'JetBrains Mono', monospace;
    }
    
    .section {
      margin-bottom: 40px;
    }
    
    .section-title {
      font-size: 14px;
      font-weight: 700;
      text-transform: uppercase;
      color: #6b7280;
      letter-spacing: 0.8px;
      margin-bottom: 18px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .section-title::before {
      content: '';
      width: 3px;
      height: 16px;
      background: linear-gradient(180deg, #10b981 0%, #059669 100%);
      border-radius: 2px;
    }
    
    .grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 18px;
      margin-bottom: 28px;
    }
    
    .grid-2 {
      grid-template-columns: repeat(2, 1fr);
    }
    
    .metric-card {
      padding: 24px;
      border-radius: 12px;
      background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
      border: 1px solid #e2e8f0;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
      transition: all 0.3s ease;
    }
    
    .metric-card:hover {
      border-color: #cbd5e1;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    }
    
    .metric-label {
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.6px;
      text-transform: uppercase;
      color: #64748b;
      margin-bottom: 12px;
    }
    
    .metric-value {
      font-size: 36px;
      font-weight: 800;
      color: #0d1117;
      line-height: 1;
      margin-bottom: 6px;
    }
    
    .metric-sub {
      font-size: 12px;
      color: #78716c;
      font-weight: 500;
    }
    
    .meta-list {
      display: grid;
      gap: 14px;
      padding: 24px;
      border-radius: 12px;
      background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%);
      border: 1px solid #e5e7eb;
    }
    
    .meta-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 24px;
      font-size: 14px;
      padding: 10px 0;
      border-bottom: 1px solid #e5e7eb;
    }
    
    .meta-row:last-child {
      border-bottom: none;
    }
    
    .meta-row .label {
      color: #6b7280;
      font-weight: 500;
      flex: 1;
    }
    
    .meta-row .value {
      color: #1f2937;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
      padding: 4px 12px;
      background: white;
      border-radius: 6px;
    }
    
    table {
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      border-radius: 12px;
      overflow: hidden;
      background: white;
      border: 1px solid #e5e7eb;
      font-size: 13px;
    }
    
    thead {
      background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
    }
    
    th {
      padding: 16px 18px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: #374151;
      text-align: left;
      border-bottom: 2px solid #d1d5db;
    }
    
    td {
      padding: 14px 18px;
      border-bottom: 1px solid #f0f0f0;
    }
    
    tbody tr:nth-child(even) {
      background: linear-gradient(90deg, #fafbfc 0%, #f8f9fa 100%);
    }
    
    tbody tr:hover {
      background: linear-gradient(90deg, #f0f4f8 0%, #f0f4f8 100%);
    }
    
    tbody tr:last-child td {
      border-bottom: none;
    }
    
    .pill {
      display: inline-block;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.4px;
      white-space: nowrap;
    }
    
    .pill.active {
      background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
      color: #166534;
      border: 1px solid #86efac;
    }
    
    .pill.inactive {
      background: linear-gradient(135deg, #fef3c7 0%, #fcd34d 100%);
      color: #92400e;
      border: 1px solid #fde047;
    }
    
    .pill.admin {
      background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%);
      color: #1e40af;
      border: 1px solid #93c5fd;
    }
    
    .summary-stats {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      padding: 24px;
      background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
      border-radius: 12px;
      border: 1px solid #a7f3d0;
      margin: 24px 0;
    }
    
    .stat-item {
      text-align: center;
    }
    
    .stat-item .stat-value {
      font-size: 28px;
      font-weight: 800;
      color: #065f46;
    }
    
    .stat-item .stat-label {
      font-size: 12px;
      color: #047857;
      font-weight: 600;
      margin-top: 4px;
    }
    
    .footer {
      margin-top: 40px;
      padding-top: 24px;
      border-top: 1px solid #e5e7eb;
      text-align: center;
      font-size: 12px;
      color: #9ca3af;
    }
    
    .footer .logo {
      font-size: 14px;
      font-weight: 700;
      color: #059669;
      margin-bottom: 8px;
    }
    
    @media print {
      body {
        background: white;
      }
      .page {
        max-width: 100%;
        padding: 0;
      }
      .report-shell {
        box-shadow: none;
        border: none;
        padding: 40px;
      }
    }
  </style>
`;

const wrapDocument = (content) => `
  <!DOCTYPE html>
  <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Raahi Report</title>
      ${baseStyles}
    </head>
    <body>
      <main class="page">
        <section class="report-shell">
          ${content}
        </section>
      </main>
    </body>
  </html>
`;

export const renderAnalyticsReport = (report) => wrapDocument(`
  <header class="header">
    <div class="header-left">
      <h1>Raahi Analytics</h1>
      <div class="subtitle">System-wide performance & sustainability metrics</div>
    </div>
    <div class="timestamp-box">
      <div class="label">Report Generated</div>
      <div class="value">${report.generatedAt}</div>
    </div>
  </header>

  <section class="section">
    <div class="section-title">Platform Overview</div>
    <div class="grid">
      <article class="metric-card">
        <div class="metric-label">Total Users</div>
        <div class="metric-value">${report.analytics.totalUsers}</div>
        <div class="metric-sub">Active members</div>
      </article>
      <article class="metric-card">
        <div class="metric-label">Trips Logged</div>
        <div class="metric-value">${report.analytics.tripsLogged}</div>
        <div class="metric-sub">Total journeys</div>
      </article>
      <article class="metric-card">
        <div class="metric-label">CO2 Saved</div>
        <div class="metric-value">${Math.round(report.analytics.co2Saved / 1000)}</div>
        <div class="metric-sub">kg total</div>
      </article>
      <article class="metric-card">
        <div class="metric-label">Air Quality</div>
        <div class="metric-value">${report.analytics.aqi}</div>
        <div class="metric-sub">Average AQI</div>
      </article>
    </div>
  </section>

  <section class="section">
    <div class="section-title">Environmental Impact</div>
    <div class="summary-stats">
      <div class="stat-item">
        <div class="stat-value">${(report.analytics.co2Saved / 1000).toFixed(2)}</div>
        <div class="stat-label">Total CO2 Eliminated (kg)</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">${Math.round(report.analytics.tripsLogged / Math.max(report.analytics.totalUsers, 1))}</div>
        <div class="stat-label">Avg Trips per User</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">${(report.analytics.co2Saved / Math.max(report.analytics.tripsLogged, 1)).toFixed(1)}</div>
        <div class="stat-label">CO2 per Trip (g)</div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="section-title">ML Model Performance</div>
    <div class="grid">
      <article class="metric-card">
        <div class="metric-label">Accuracy</div>
        <div class="metric-value">${report.modelMetrics.accuracy}%</div>
        <div class="metric-sub">Prediction accuracy</div>
      </article>
      <article class="metric-card">
        <div class="metric-label">Precision</div>
        <div class="metric-value">${report.modelMetrics.precision}%</div>
        <div class="metric-sub">True positive rate</div>
      </article>
      <article class="metric-card">
        <div class="metric-label">Recall</div>
        <div class="metric-value">${report.modelMetrics.recall}%</div>
        <div class="metric-sub">Coverage rate</div>
      </article>
      <article class="metric-card">
        <div class="metric-label">F1 Score</div>
        <div class="metric-value">${report.modelMetrics.f1Score}%</div>
        <div class="metric-sub">Overall health</div>
      </article>
    </div>
    
    <div class="meta-list">
      <div class="meta-row">
        <span class="label">Model Version</span>
        <span class="value">${report.modelMetrics.version}</span>
      </div>
      <div class="meta-row">
        <span class="label">Training Samples</span>
        <span class="value">${report.modelMetrics.trainingSamples}</span>
      </div>
    </div>
  </section>

  <footer class="footer">
    <div class="logo">🌱 Raahi</div>
    <p>Sustainable urban mobility platform | Data confidential</p>
  </footer>
`);


export const renderUsersReport = (report) => wrapDocument(`
  <header class="header">
    <div class="header-left">
      <h1>User Directory</h1>
      <div class="subtitle">Complete platform user roster & sustainability scores</div>
    </div>
    <div class="timestamp-box">
      <div class="label">Report Generated</div>
      <div class="value">${report.generatedAt}</div>
    </div>
  </header>

  <section class="section">
    <div class="section-title">Platform Users</div>
    <div class="summary-stats">
      <div class="stat-item">
        <div class="stat-value">${report.users.length}</div>
        <div class="stat-label">Total Users</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">${report.users.filter(u => u.activity === 'Active').length}</div>
        <div class="stat-label">Active Users</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">${report.users.filter(u => u.role === 'Admin').length}</div>
        <div class="stat-label">Administrators</div>
      </div>
    </div>
  </section>

  <section class="section">
    <div class="section-title">User Details</div>
    <table>
      <thead>
        <tr>
          <th style="width: 18%">Name</th>
          <th style="width: 16%">Contact</th>
          <th style="width: 8%">Trips</th>
          <th style="width: 12%">Status</th>
          <th style="width: 8%">Role</th>
          <th style="width: 12%">CO2 Saved</th>
          <th style="width: 12%">Savings</th>
          <th style="width: 14%">Member Since</th>
        </tr>
      </thead>
      <tbody>
        ${report.users.map((user) => `
          <tr>
            <td><strong>${user.name}</strong></td>
            <td style="font-size: 12px; color: #666; font-family: 'JetBrains Mono', monospace;">${user.contact}</td>
            <td><strong>${user.trips}</strong></td>
            <td><span class="pill ${user.activity === 'Active' ? 'active' : 'inactive'}">${user.activity}</span></td>
            <td><span class="pill ${user.role === 'Admin' ? 'admin' : 'pill.user'}" style="background: #e0e7ff; color: #3730a3; border: 1px solid #c7d2fe;">${user.role}</span></td>
            <td><strong>${user.co2Saved}</strong> kg</td>
            <td><strong>₹${user.moneySaved}</strong></td>
            <td style="font-size: 12px; color: #666;">${user.joinedDate}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  </section>

  <section class="section">
    <div class="section-title">Summary Statistics</div>
    <div class="meta-list">
      <div class="meta-row">
        <span class="label">Total CO2 Offset (all users)</span>
        <span class="value">${(report.users.reduce((sum, u) => sum + parseFloat(u.co2Saved), 0)).toFixed(1)} kg</span>
      </div>
      <div class="meta-row">
        <span class="label">Total Money Saved</span>
        <span class="value">₹${(report.users.reduce((sum, u) => sum + parseFloat(u.moneySaved), 0)).toFixed(2)}</span>
      </div>
      <div class="meta-row">
        <span class="label">Total Trips Logged</span>
        <span class="value">${report.users.reduce((sum, u) => sum + u.trips, 0)}</span>
      </div>
      <div class="meta-row">
        <span class="label">Average CO2 per User</span>
        <span class="value">${(report.users.reduce((sum, u) => sum + parseFloat(u.co2Saved), 0) / Math.max(report.users.length, 1)).toFixed(1)} kg</span>
      </div>
    </div>
  </section>

  <footer class="footer">
    <div class="logo">🌱 Raahi</div>
    <p>Sustainable urban mobility platform | Data confidential</p>
  </footer>
`);

