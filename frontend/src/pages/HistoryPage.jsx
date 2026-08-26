/**
 * SevaSetu AI — History Page
 * Author: Rahul Jha | Made in India 🇮🇳
 */

import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { queryAPI, reportAPI } from "../services/api";
import { useToast } from "../components/MainLayout";
import styles from "./HistoryPage.module.css";

const MOCK_HISTORY = [
  { id:1, question:"How to correct name in Voter ID card?", ai_response:"To correct your Voter ID name, submit Form 8 at voters.eci.gov.in or nearest ERO office. Documents: current Voter ID, name proof (Aadhaar/PAN). Processing takes 30-45 days. You can also do it offline at BLO office.", category:"voter_id", language:"en", confidence:0.92, created_at:new Date(Date.now()-7200000).toISOString() },
  { id:2, question:"Documents required for PAN card for student?", ai_response:"PAN card for students: 1) Aadhaar card (identity+address), 2) DOB proof (birth certificate/10th marksheet), 3) 2 passport photos, 4) Form 49A. Apply at tin.tin.nsdl.com. Fee: ₹107. Delivered in 15-20 working days.", category:"pan_card", language:"en", confidence:0.89, created_at:new Date(Date.now()-86400000).toISOString() },
  { id:3, question:"Ayushman Bharat eligibility kaise check karein?", ai_response:"Ayushman Bharat eligibility check: 1) pmjay.gov.in पर जाएं, 2) 'Am I Eligible' पर क्लिक करें, 3) Aadhaar number या ration card number डालें, 4) OTP verify करें। Toll-free: 14555 पर call करें।", category:"health_scheme", language:"hi", confidence:0.87, created_at:new Date(Date.now()-172800000).toISOString() },
  { id:4, question:"Tatkal passport vs normal passport difference?", ai_response:"Normal Passport: 30-45 days, ₹1,500-2,000. Tatkal: 1-3 days, extra ₹3,500. Tatkal needs urgency proof (ticket/medical). Both require same documents: Aadhaar, Birth Cert, 10th Certificate, address proof. Apply at passportindia.gov.in", category:"passport", language:"en", confidence:0.91, created_at:new Date(Date.now()-259200000).toISOString() },
  { id:5, question:"PM Kisan Yojana registration process?", ai_response:"PM Kisan registration: 1) Visit pmkisan.gov.in, 2) Click 'New Farmer Registration', 3) Enter Aadhaar, land records (7/12), bank details, 4) OTP verify and submit. Or visit CSC center. Get ₹2,000 every 4 months. Helpline: 155261", category:"agriculture_scheme", language:"en", confidence:0.94, created_at:new Date(Date.now()-345600000).toISOString() },
  { id:6, question:"Domicile certificate Maharashtra online?", ai_response:"Maharashtra domicile certificate: 1) aaplesarkar.mahaonline.gov.in, 2) Revenue → Domicile Certificate, 3) Upload: Aadhaar, school certificates, ration card, address proof, 4) Pay ₹50-100, 5) 15-30 days processing. Valid permanently for birth domicile.", category:"domicile_certificate", language:"en", confidence:0.86, created_at:new Date(Date.now()-432000000).toISOString() },
];

const CAT_LABELS = { voter_id:"Voter ID", pan_card:"PAN Card", passport:"Passport", health_scheme:"Health", agriculture_scheme:"Agriculture", housing_scheme:"Housing", education_scheme:"Education", domicile_certificate:"Domicile", income_certificate:"Income Cert", caste_certificate:"Caste Cert", general:"General" };
const CAT_COLORS = { voter_id:"saffron", pan_card:"green", passport:"blue", health_scheme:"green", agriculture_scheme:"green", housing_scheme:"blue", education_scheme:"gold", general:"gold" };

export default function HistoryPage() {
  const navigate  = useNavigate();
  const showToast = useToast();

  const [history,     setHistory]     = useState([]);
  const [loading,     setLoading]     = useState(true);
  const [search,      setSearch]      = useState("");
  const [catFilter,   setCatFilter]   = useState("all");
  const [expanded,    setExpanded]    = useState(null);
  const [page,        setPage]        = useState(1);
  const [total,       setTotal]       = useState(0);
  const [deleting,    setDeleting]    = useState(null);
  const LIMIT = 10;

  const loadHistory = useCallback(async () => {
    setLoading(true);
    try {
      const res = await queryAPI.getHistory(page, LIMIT, catFilter === "all" ? null : catFilter, search || null);
      setHistory(res.data.data || []);
      setTotal(res.data.total || 0);
    } catch {
      setHistory(MOCK_HISTORY);
      setTotal(MOCK_HISTORY.length);
    } finally {
      setLoading(false);
    }
  }, [page, catFilter, search]);

  useEffect(() => {
    const t = setTimeout(loadHistory, 350);
    return () => clearTimeout(t);
  }, [loadHistory]);

  const handleDelete = async (id) => {
    setDeleting(id);
    try {
      await queryAPI.deleteQuery(id);
      setHistory(h => h.filter(q => q.id !== id));
      showToast?.("Query deleted", "success");
    } catch {
      showToast?.("Failed to delete", "error");
    } finally {
      setDeleting(null);
    }
  };

  const handleExport = async (id) => {
    try {
      await reportAPI.downloadQueryPDF(id);
      showToast?.("PDF downloaded!", "success");
    } catch {
      showToast?.("PDF generation failed", "error");
    }
  };

  const handleExportAll = async () => {
    try {
      await reportAPI.downloadHistoryPDF();
      showToast?.("History PDF downloaded!", "success");
    } catch {
      showToast?.("Export failed", "error");
    }
  };

  const toggleExpand = (id) => setExpanded(e => e === id ? null : id);

  const categories = ["all", ...new Set(MOCK_HISTORY.map(q => q.category))];

  return (
    <div className={styles.historyPage}>
      {/* Header */}
      <div className={styles.pageHeader}>
        <div>
          <h1>📝 Query History</h1>
          <p className="text-muted">{total} total interactions with SevaSetu AI</p>
        </div>
        <button className="btn btn-secondary" onClick={handleExportAll}>
          📥 Export All PDF
        </button>
      </div>

      {/* Search + Filter */}
      <div style={{ display: "flex", gap: 10, marginBottom: 14, flexWrap: "wrap" }}>
        <div className="search-bar" style={{ flex: 1, minWidth: 200 }}>
          <span>🔍</span>
          <input
            type="text"
            placeholder="Search questions..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
          {search && <button style={{ background: "none", border: "none", color: "var(--text-2)", cursor: "pointer" }} onClick={() => setSearch("")}>✕</button>}
        </div>
        <select
          className="form-select"
          style={{ width: "auto", minWidth: 140 }}
          value={catFilter}
          onChange={(e) => { setCatFilter(e.target.value); setPage(1); }}
        >
          <option value="all">All Categories</option>
          {categories.filter(c => c !== "all").map(c => (
            <option key={c} value={c}>{CAT_LABELS[c] || c}</option>
          ))}
        </select>
      </div>

      {/* History list */}
      {loading ? (
        <div>
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="skeleton" style={{ height: 60, marginBottom: 10, borderRadius: 12 }} />
          ))}
        </div>
      ) : history.length === 0 ? (
        <div className="empty-state">
          <div className="icon">💬</div>
          <h3>No queries found</h3>
          <p>{search ? "Try different search terms" : "Start chatting with SevaSetu AI!"}</p>
          <button className="btn btn-primary btn-sm" onClick={() => navigate("/chat")}>Ask AI Now →</button>
        </div>
      ) : (
        <div className={styles.historyList}>
          {history.map((q) => {
            const catColor = CAT_COLORS[q.category] || "blue";
            const catLabel = CAT_LABELS[q.category] || "General";
            const isOpen   = expanded === q.id;
            const timeStr  = new Date(q.created_at).toLocaleString("en-IN", {
              day: "2-digit", month: "short", year: "numeric",
              hour: "2-digit", minute: "2-digit",
            });

            return (
              <div key={q.id} className={`${styles.histCard} ${isOpen ? styles.histCardOpen : ""}`}>
                {/* Header row */}
                <div className={styles.histHead} onClick={() => toggleExpand(q.id)}>
                  <span className={`badge badge-${catColor}`}>{catLabel}</span>
                  <span className={styles.histQ}>{q.question}</span>
                  <div className={styles.histMeta}>
                    <span className={styles.histTime}>{timeStr}</span>
                    {q.language && q.language !== "en" && (
                      <span className="badge badge-gold" style={{ fontSize: "0.65rem" }}>
                        {q.language === "hi" ? "हिंदी" : "मराठी"}
                      </span>
                    )}
                    {q.confidence > 0 && (
                      <span className="badge badge-green" style={{ fontSize: "0.65rem" }}>
                        {Math.round(q.confidence * 100)}%
                      </span>
                    )}
                    <span className={styles.chevron}>{isOpen ? "▲" : "▼"}</span>
                  </div>
                </div>

                {/* Expanded answer */}
                {isOpen && (
                  <div className={styles.histBody}>
                    <div className={styles.answerLabel}>🤖 SevaSetu AI Response:</div>
                    <div className={styles.answerText}>{q.ai_response}</div>
                    <div className={styles.histActions}>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => navigate("/chat", { state: { prefillQuery: q.question } })}
                      >
                        💬 Ask Again
                      </button>
                      <button className="btn btn-secondary btn-sm" onClick={() => handleExport(q.id)}>
                        📥 Download PDF
                      </button>
                      <button
                        className="btn btn-ghost btn-sm"
                        style={{ color: "var(--error)" }}
                        onClick={() => handleDelete(q.id)}
                        disabled={deleting === q.id}
                      >
                        {deleting === q.id ? "..." : "🗑️ Delete"}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Pagination */}
      {total > LIMIT && (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 16, padding: "16px 0" }}>
          <button className="btn btn-secondary btn-sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>← Previous</button>
          <span className="text-muted">Page {page} of {Math.ceil(total / LIMIT)}</span>
          <button className="btn btn-secondary btn-sm" disabled={page >= Math.ceil(total / LIMIT)} onClick={() => setPage(p => p + 1)}>Next →</button>
        </div>
      )}
    </div>
  );
}
