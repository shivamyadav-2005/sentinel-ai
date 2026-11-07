
import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

const detailPanelStyle = {
  marginTop: "12px",
  padding: "14px",
  border: "1px solid var(--border-color, #2d3748)",
  borderRadius: "10px",
  background: "var(--panel-background, #111827)",
  lineHeight: 1.6,
};

const analystPanelStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "16px",
};

const chatMessagesStyle = {
  display: "flex",
  flexDirection: "column",
  gap: "12px",
  maxHeight: "450px",
  overflowY: "auto",
  padding: "12px 0",
};

const suggestedQuestions = [
  "Which security issue should I fix first?",
  "Explain my highest-risk finding.",
  "How can I fix this issue?",
  "Summarize my latest scan.",
];

function App() {
  const [region, setRegion] = useState("ap-south-1");
  const [scanName, setScanName] = useState("SentinelAI Security Audit");
  const [scan, setScan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [analystQuestion, setAnalystQuestion] = useState("");
  const [analystMessages, setAnalystMessages] = useState([]);
  const [analystLoading, setAnalystLoading] = useState(false);
  const [analystError, setAnalystError] = useState("");

  async function runScan(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setScan(null);
    setAnalystMessages([]);
    setAnalystError("");

    try {
      const response = await fetch(`${API_URL}/scans/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          region: region.trim(),
          scan_name: scanName.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg).join(", ")
          : data.detail || data.error?.message || "The scan request failed.";

        throw new Error(detail);
      }

      setScan(data);
    } catch (err) {
      setError(
        err instanceof TypeError
          ? "Cannot connect to the API. Make sure the SentinelAI backend is running."
          : err.message,
      );
    } finally {
      setLoading(false);
    }
  }

  const findings = scan?.findings ?? [];

  const warningCount = findings.filter(
    (finding) => finding.status === "WARNING",
  ).length;

  const passedCount = findings.filter(
    (finding) => finding.status === "PASS",
  ).length;

  const highCount = findings.filter(
    (finding) => finding.severity === "HIGH",
  ).length;

  function downloadReport() {
    if (!scan) return;

    const report = {
      generated_at: new Date().toISOString(),
      ...scan,
    };

    const blob = new Blob([JSON.stringify(report, null, 2)], {
      type: "application/json",
    });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = "sentinelai-scan-report.json";
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  }

  async function sendAnalystMessage(question) {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || analystLoading) return;

    if (!scan || findings.length === 0) {
      setAnalystError("Run a security scan before asking the analyst.");
      return;
    }

    setAnalystError("");
    setAnalystQuestion("");

    setAnalystMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: trimmedQuestion,
      },
    ]);

    setAnalystLoading(true);

    try {
      const response = await fetch(`${API_URL}/analyst/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          question: trimmedQuestion,
          findings: findings,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item) => item.msg).join(", ")
          : data.detail || data.error?.message || "Analyst request failed.";

        throw new Error(detail);
      }

      setAnalystMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.answer,
          priority: data.priority,
          source: data.source,
          riskScore: data.risk_score,
          riskLevel: data.risk_level,
          riskExplanation: data.risk_explanation,
        },
      ]);
    } catch (err) {
      setAnalystError(
        err instanceof TypeError
          ? "Cannot connect to the Analyst API. Check that the backend is running."
          : err.message,
      );
    } finally {
      setAnalystLoading(false);
    }
  }

  function handleAnalystSubmit(event) {
    event.preventDefault();
    sendAnalystMessage(analystQuestion);
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#overview" aria-label="SentinelAI home">
          <span className="brand-mark">S</span>
          <span>
            <strong>SentinelAI</strong>
            <small>Cloud Security Platform</small>
          </span>
        </a>

        <div className="sidebar-label">WORKSPACE</div>

        <nav className="navigation">
          <a className="nav-link active" href="#overview">
            <span>▦</span> Overview
          </a>
          <a className="nav-link" href="#scanner">
            <span>⌕</span> Security Scanner
          </a>
          <a className="nav-link" href="#findings">
            <span>◈</span> Findings
          </a>
          <a className="nav-link" href="#analyst">
            <span>✧</span> Analyst Mode
          </a>
        </nav>

        <div className="sidebar-bottom">
          <div className="connection-indicator">
            <span className="status-dot" />
            <div>
              <strong>Local environment</strong>
              <small>Mock data mode</small>
            </div>
          </div>
          <p>SentinelAI · Development</p>
        </div>
      </aside>

      <main className="main-content" id="overview">
        <header className="topbar">
          <div className="breadcrumb">
            Workspace <span>/</span> <strong>Overview</strong>
          </div>
          <div className="environment-pill">
            <span className="status-dot" /> DEVELOPMENT
          </div>
        </header>

        <section className="page-heading">
          <div>
            <p className="eyebrow">CLOUD SECURITY INTELLIGENCE</p>
            <h1>Security overview</h1>
            <p className="page-description">
              Scan cloud configurations and review security findings in one
              place.
            </p>
          </div>
          <div className="scan-mode">
            <span className="mode-icon">◇</span>
            <span>
              <strong>Demo environment</strong>
              <small>No live AWS connection</small>
            </span>
          </div>
        </section>

        <section className="stats-grid" aria-label="Scan statistics">
          <article className="stat-card">
            <div className="stat-top">
              <span>Total findings</span>
              <span className="stat-icon purple">◈</span>
            </div>
            <strong className="stat-value">{scan ? findings.length : "—"}</strong>
            <p>{scan ? "From the latest scan" : "Run a scan to begin"}</p>
          </article>

          <article className="stat-card">
            <div className="stat-top">
              <span>High severity</span>
              <span className="stat-icon red">!</span>
            </div>
            <strong className="stat-value">{scan ? highCount : "—"}</strong>
            <p className="muted">Requires security review</p>
          </article>

          <article className="stat-card">
            <div className="stat-top">
              <span>Warnings</span>
              <span className="stat-icon amber">△</span>
            </div>
            <strong className="stat-value">{scan ? warningCount : "—"}</strong>
            <p className="muted">Checks requiring attention</p>
          </article>

          <article className="stat-card">
            <div className="stat-top">
              <span>Checks passed</span>
              <span className="stat-icon green">✓</span>
            </div>
            <strong className="stat-value">{scan ? passedCount : "—"}</strong>
            <p className="muted">Checks that passed</p>
          </article>
        </section>

        <section className="content-grid">
          <article className="panel scan-panel" id="scanner">
            <div className="panel-heading">
              <div>
                <h2>Run a security scan</h2>
                <p>Configure a scan using the local demo dataset.</p>
              </div>
              <span className="panel-symbol">⌘</span>
            </div>

            <form className="scan-form" onSubmit={runScan}>
              <label htmlFor="scan-name">Scan name</label>
              <input
                id="scan-name"
                value={scanName}
                onChange={(event) => setScanName(event.target.value)}
                maxLength={100}
                required
                placeholder="e.g. Production security audit"
              />

              <label htmlFor="region">Cloud region</label>
              <select
                id="region"
                value={region}
                onChange={(event) => setRegion(event.target.value)}
                required
              >
                <option value="ap-south-1">Asia Pacific · Mumbai</option>
                <option value="us-east-1">US East · N. Virginia</option>
                <option value="us-west-2">US West · Oregon</option>
                <option value="eu-west-1">Europe · Ireland</option>
              </select>

              <div className="form-note">
                <span>ⓘ</span>
                This scan uses sample S3 configuration data. The selected
                region is recorded but no AWS resources are contacted.
              </div>

              <button
                className="primary-button"
                type="submit"
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner" /> Scanning...
                  </>
                ) : (
                  <>
                    Run security scan <span>→</span>
                  </>
                )}
              </button>
            </form>

            {error && (
              <div className="error-message" role="alert">
                <strong>Scan failed</strong>
                <p>{error}</p>
              </div>
            )}
          </article>

          <article className="panel status-panel">
            <div className="panel-heading">
              <div>
                <h2>Scanner status</h2>
                <p>Current application connectivity.</p>
              </div>
              <span className="status-dot large" />
            </div>

            <div className="service-row">
              <span className="service-icon">API</span>
              <span className="service-copy">
                <strong>SentinelAI API</strong>
                <small>FastAPI · localhost:8000</small>
              </span>
              <span className="service-badge">Local</span>
            </div>

            <div className="service-row">
              <span className="service-icon">S3</span>
              <span className="service-copy">
                <strong>S3 analysis engine</strong>
                <small>Local security rules</small>
              </span>
              <span className="service-badge">Available</span>
            </div>

            <div className="service-row">
              <span className="service-icon">AI</span>
              <span className="service-copy">
                <strong>Analyst engine</strong>
                <small>Local rule-based analysis</small>
              </span>
              <span className="service-badge">Available</span>
            </div>

            <div className="notice-box">
              <span>ⓘ</span>
              <p>
                Analyst responses use local rules and supplied mock scan
                findings. AWS and external AI integrations are not active.
              </p>
            </div>
          </article>
        </section>

        <section className="panel findings-panel" id="findings">
          <div className="panel-heading findings-heading">
            <div>
              <h2>Security findings</h2>
              <p>
                {scan
                  ? `Results for ${scan.scan.scan_name}`
                  : "Run a scan to populate the findings table."}
              </p>
            </div>
            <button
              className="secondary-button"
              type="button"
              onClick={downloadReport}
              disabled={!scan}
            >
              ↓ Export JSON
            </button>
          </div>

          {!scan && !loading && (
            <div className="empty-state">
              <div className="empty-icon">⌕</div>
              <strong>No scan results yet</strong>
              <p>Run a security scan to see findings here.</p>
            </div>
          )}

          {loading && (
            <div className="empty-state">
              <span className="spinner dark-spinner" />
              <strong>Analyzing mock security configuration...</strong>
            </div>
          )}

          {scan && (
            <>
              <div className="scan-meta">
                <span>
                  <span className="status-dot" /> Completed
                </span>
                <span>Region: {scan.scan.region}</span>
                <span>Source: {scan.source}</span>
              </div>

              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>SECURITY CHECK</th>
                      <th>STATUS</th>
                      <th>SEVERITY</th>
                      <th>MESSAGE &amp; GUIDANCE</th>
                    </tr>
                  </thead>
                  <tbody>
                    {findings.map((finding, index) => (
                      <tr key={`${finding.check}-${index}`}>
                        <td>
                          <strong>
                            {finding.check.replaceAll("_", " ")}
                          </strong>
                          <small>{finding.bucket_name}</small>
                        </td>
                        <td>
                          <span
                            className={`result-badge ${
                              finding.status === "PASS" ? "pass" : "warning"
                            }`}
                          >
                            {finding.status}
                          </span>
                        </td>
                        <td>
                          <span
                            className={`severity-badge ${finding.severity.toLowerCase()}`}
                          >
                            {finding.severity}
                          </span>
                        </td>
                        <td className="message-cell">
                          <p>{finding.message}</p>

                          <details style={{ marginTop: "10px" }}>
                            <summary
                              style={{
                                cursor: "pointer",
                                fontWeight: 600,
                                padding: "6px 0",
                              }}
                            >
                              View explanation &amp; remediation
                            </summary>

                            <div style={detailPanelStyle}>
                              <h4>Explanation</h4>
                              <p>{finding.explanation}</p>

                              <h4 style={{ marginTop: "14px" }}>
                                Potential impact
                              </h4>
                              <p>{finding.potential_impact}</p>

                              <h4 style={{ marginTop: "14px" }}>
                                Recommended remediation
                              </h4>
                              <ol style={{ paddingLeft: "22px" }}>
                                {(finding.remediation ?? []).map(
                                  (step, stepIndex) => (
                                    <li
                                      key={stepIndex}
                                      style={{ marginBottom: "7px" }}
                                    >
                                      {step}
                                    </li>
                                  ),
                                )}
                              </ol>

                              <p
                                style={{
                                  marginTop: "12px",
                                  fontSize: "0.85em",
                                  opacity: 0.8,
                                }}
                              >
                                Guidance is rule-based and based on mock data.
                                Verify the actual AWS configuration before
                                making changes.
                              </p>
                            </div>
                          </details>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <p className="results-disclaimer">
                These are mock-data results for development. They do not
                confirm the security posture of any real AWS account.
              </p>
            </>
          )}
        </section>

        <section className="panel" id="analyst" style={{ marginTop: "24px" }}>
          <div className="panel-heading">
            <div>
              <p className="eyebrow">SENTINELAI INTELLIGENCE</p>
              <h2>Security Analyst</h2>
              <p>
                Ask questions about findings from your latest security scan.
              </p>
            </div>
            <span className="service-badge">Rule-based</span>
          </div>

          <div style={analystPanelStyle}>
            <div
              style={{
                padding: "12px 14px",
                borderRadius: "10px",
                background: "var(--panel-background, #111827)",
                border: "1px solid var(--border-color, #2d3748)",
                fontSize: "0.9rem",
                lineHeight: 1.6,
              }}
            >
              <strong>Analysis mode: Local rule-based engine</strong>
              <p style={{ marginTop: "5px" }}>
                This analyst uses the findings supplied from your latest
                mock-data scan. It does not use an external AI model or connect
                to AWS.
              </p>
            </div>

            {!scan && (
              <div className="empty-state">
                <strong>Scan required</strong>
                <p>
                  Run a security scan first. The analyst will then be able to
                  answer questions about its findings.
                </p>
              </div>
            )}

            {scan && (
              <>
                <div style={chatMessagesStyle} aria-live="polite">
                  {analystMessages.length === 0 && (
                    <div
                      style={{
                        alignSelf: "flex-start",
                        maxWidth: "85%",
                        padding: "14px",
                        borderRadius: "12px",
                        background: "var(--panel-background, #111827)",
                        border: "1px solid var(--border-color, #2d3748)",
                        lineHeight: 1.6,
                      }}
                    >
                      <strong>SentinelAI Analyst</strong>
                      <p style={{ marginTop: "6px" }}>
                        Your latest scan has {findings.length} findings,
                        including {highCount} HIGH severity findings. What
                        would you like to understand?
                      </p>
                    </div>
                  )}

                  {analystMessages.map((message, index) => (
                    <div
                      key={`${message.role}-${index}`}
                      style={{
                        alignSelf:
                          message.role === "user" ? "flex-end" : "flex-start",
                        maxWidth: "85%",
                        padding: "14px",
                        borderRadius: "12px",
                        background:
                          message.role === "user"
                            ? "var(--accent-color, #4338ca)"
                            : "var(--panel-background, #111827)",
                        color: message.role === "user" ? "#ffffff" : "inherit",
                        border:
                          message.role === "assistant"
                            ? "1px solid var(--border-color, #2d3748)"
                            : "none",
                        lineHeight: 1.6,
                        whiteSpace: "pre-wrap",
                      }}
                    >
                      <strong>
                        {message.role === "user"
                          ? "You"
                          : "SentinelAI Analyst"}
                      </strong>
                      <p style={{ marginTop: "6px" }}>{message.content}</p>

                      {message.role === "assistant" &&
                        message.riskScore !== null &&
                        message.riskScore !== undefined && (
                          <div
                            style={{
                              marginTop: "12px",
                              padding: "12px",
                              borderRadius: "10px",
                              border: "1px solid var(--border-color, #2d3748)",
                              background: "rgba(127, 127, 127, 0.08)",
                            }}
                          >
                            <div
                              style={{
                                display: "flex",
                                justifyContent: "space-between",
                                alignItems: "center",
                                gap: "12px",
                                flexWrap: "wrap",
                              }}
                            >
                              <strong>Finding risk score</strong>
                              <span
                                className={`severity-badge ${(message.riskLevel || "info").toLowerCase()}`}
                              >
                                {message.riskLevel || "INFO"}
                              </span>
                            </div>

                            <div
                              style={{
                                display: "flex",
                                alignItems: "baseline",
                                gap: "5px",
                                marginTop: "8px",
                              }}
                            >
                              <strong style={{ fontSize: "1.7rem" }}>
                                {message.riskScore}
                              </strong>
                              <span style={{ opacity: 0.7 }}>/ 100</span>
                            </div>

                            {message.riskExplanation && (
                              <p style={{ marginTop: "8px", fontSize: "0.88rem" }}>
                                {message.riskExplanation}
                              </p>
                            )}

                            <p
                              style={{
                                marginTop: "8px",
                                fontSize: "0.75rem",
                                opacity: 0.7,
                              }}
                            >
                              Prototype heuristic score based on severity and
                              finding status; not a probability or validated
                              industry risk rating.
                            </p>
                          </div>
                        )}

                      {message.role === "assistant" && (
                        <div
                          style={{
                            marginTop: "10px",
                            fontSize: "0.78rem",
                            opacity: 0.75,
                          }}
                        >
                          Priority: {message.priority} · Source:{" "}
                          {message.source}
                        </div>
                      )}
                    </div>
                  ))}

                  {analystLoading && (
                    <div
                      style={{
                        alignSelf: "flex-start",
                        padding: "12px",
                        borderRadius: "10px",
                        background: "var(--panel-background, #111827)",
                      }}
                    >
                      Analyst is reviewing your findings...
                    </div>
                  )}
                </div>

                <div>
                  <strong style={{ display: "block", marginBottom: "10px" }}>
                    Suggested questions
                  </strong>
                  <div
                    style={{
                      display: "flex",
                      flexWrap: "wrap",
                      gap: "8px",
                    }}
                  >
                    {suggestedQuestions.map((question) => (
                      <button
                        key={question}
                        type="button"
                        className="secondary-button"
                        disabled={analystLoading}
                        onClick={() => sendAnalystMessage(question)}
                      >
                        {question}
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}

            {analystError && (
              <div className="error-message" role="alert">
                <strong>Analyst request failed</strong>
                <p>{analystError}</p>
              </div>
            )}

            <form
              onSubmit={handleAnalystSubmit}
              style={{
                display: "flex",
                gap: "10px",
                alignItems: "stretch",
                flexWrap: "wrap",
              }}
            >
              <input
                type="text"
                value={analystQuestion}
                onChange={(event) => setAnalystQuestion(event.target.value)}
                placeholder={
                  scan
                    ? "Ask about your security findings..."
                    : "Run a scan to start chatting..."
                }
                maxLength={1000}
                disabled={!scan || analystLoading}
                style={{ flex: "1 1 250px", minWidth: 0 }}
              />
              <button
                className="primary-button"
                type="submit"
                disabled={
                  !scan || analystLoading || !analystQuestion.trim()
                }
              >
                {analystLoading ? "Analyzing..." : "Send message →"}
              </button>
            </form>

            <p style={{ fontSize: "0.82rem", opacity: 0.75 }}>
              Demo limitation: responses are generated by deterministic local
              rules. Always verify security recommendations against your real
              AWS configuration.
            </p>
          </div>
        </section>

        <footer className="footer">
          <span>SentinelAI · Cloud Security MVP</span>
          <span>Built for security visibility and analysis</span>
        </footer>
      </main>
    </div>
  );
}

export default App;
