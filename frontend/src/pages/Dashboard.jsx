/**
 * SevaSetu AI — Dashboard Page
 * Author: Rahul Jha | Made in India 🇮🇳
 */

import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { queryAPI, schemeAPI, adminAPI, reportAPI } from "../services/api";
import { useAuth } from "../App";
import { useToast } from "../components/MainLayout";
import styles from "./Dashboard.module.css";

// ── Stat card ──────────────────────────────────────────────────────────────
function StatCard({ num, label, icon, color, onClick }) {
  return (
    <div className={`stat-card ${color}`} onClick={onClick} style={{ cursor: onClick ? "pointer" : "default" }}>
      <div className="stat-num">{num}</div>
      <div className="stat-lbl">{label}</div>
      <div className="stat-icon">{icon}</div>
    </div>
  );
}

// ── Recent query row ───────────────────────────────────────────────────────
function QueryRow({ query, onAskAgain, onExport }) {
  const catColors = {
    voter_id: "saffron", pan_card: "green", passport: "blue",
    health_scheme: "green", agriculture_scheme: "green", general: "gold",
  };
  const catColor = catColors[query.category] || "blue";

  return (
    <div className={styles.queryRow}>
      <span className={`badge badge-${catColor}`}>
        {(query.category || "general").replace(/_/g, " ")}
      </span>
      <span className={styles.queryText}>{query.question}</span>
      <div className={styles.queryActions}>
        <span className={styles.queryTime}>
          {new Date(query.created_at).toLocaleDateString("en-IN", { day: "2-digit", month: "short" })}
        </span>
        <button className="btn btn-ghost btn-sm" onClick={() => onAskAgain(query.question)}>💬</button>
        <button className="btn btn-ghost btn-sm" onClick={() => onExport(query.id)}>📥</button>
      </div>
    </div>
  );
}

// ── Eligible scheme row ────────────────────────────────────────────────────
function SchemeRow({ scheme }) {
  const navigate = useNavigate();
  const score    = Math.round((scheme.eligibility_score || 0) * 100);
  const status   = scheme.eligibility_status;
  const badgeClass = status === "eligible" ? "green" : status === "partial" ? "gold" : "blue";
  const icon = { eligible: "✅", partial: "⚠️", not_eligible: "❌" }[status] || "🔍";

  return (
    <div className={styles.schemeRow}>
      <div className={styles.schemeRowLeft}>
        <span className={`badge badge-${badgeClass}`}>{icon} {status?.replace("_", " ")}</span>
        <span className={styles.schemeName}>{scheme.name}</span>
      </div>
      <div className={styles.schemeRowRight}>
        <div className={styles.schemeScore}>
          <div className="progress-bar" style={{ width: 80 }}>
            <div className={`progress-fill ${badgeClass}`} style={{ width: `${score}%` }} />
          </div>
          <span className={styles.scoreText}>{score}%</span>
        </div>
        <button
          className="btn btn-secondary btn-sm"
          onClick={() => navigate("/chat", { state: { prefillQuery: `Tell me about ${scheme.name}` } })}
        >
          Learn →
        </button>
      </div>
    </div>
  );
}

// ── Quick action card ──────────────────────────────────────────────────────
const QUICK_ACTIONS = [
  { icon: "🗳️", label: "Voter ID",         query: "How to apply for Voter ID?" },
  { icon: "💳", label: "PAN Card",          query: "How to apply for PAN Card?" },
  { icon: "📘", label: "Passport",          query: "How to apply for Passport?" },
  { icon: "🌾", label: "PM Kisan",          query: "PM Kisan Yojana eligibility and how to apply?" },
  { icon: "🏥", label: "Ayushman Bharat",   query: "Ayushman Bharat PMJAY eligibility?" },
  { icon: "🏠", label: "PM Awas Yojana",    query: "PM Awas Yojana eligibility and benefits?" },
  { icon: "📜", label: "Birth Certificate", query: "How to apply for Birth Certificate?" },
  { icon: "📋", label: "Income Cert.",      query: "How to get Income Certificate?" },
];

// ── Main Dashboard ─────────────────────────────────────────────────────────
export default function Dashboard() {
  const { user }  = useAuth();
  const navigate  = useNavigate();
  const showToast = useToast();

  const [stats,         setStats]         = useState(null);
  const [recentQueries, setRecentQueries] = useState([]);
  const [eligibleSchemes, setEligibleSchemes] = useState([]);
  const [loading,       setLoading]       = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    setLoading(true);
    try {
      // Parallel fetch
      const [histRes, schemeRes] = await Promise.allSettled([
        queryAPI.getHistory(1, 5),
        schemeAPI.checkEligibility({
          state: user?.state,
          categories: ["agriculture", "health", "finance", "housing"],
        }),
      ]);

      if (histRes.status === "fulfilled") {
        setRecentQueries(histRes.value.data.data || []);
        setStats({
          totalQueries: histRes.value.data.total || 0,
        });
      }
      if (schemeRes.status === "fulfilled") {
        setEligibleSchemes(
          (schemeRes.value.data.schemes || []).filter((s) => s.eligibility_score >= 0.4).slice(0, 5)
        );
      }
    } catch {
      // Use mock data for demo
      setStats({ totalQueries: 24 });
      setRecentQueries([
        { id: 1, question: "How to correct name in Voter ID?", category: "voter_id", created_at: new Date().toISOString() },
        { id: 2, question: "PAN card documents required for student?", category: "pan_card", created_at: new Date().toISOString() },
        { id: 3, question: "Ayushman Bharat eligibility check?", category: "health_scheme", created_at: new Date().toISOString() },
      ]);
      setEligibleSchemes([
        { id: 1, name: "PM Jan Dhan Yojana", eligibility_score: 0.95, eligibility_status: "eligible" },
        { id: 2, name: "Ayushman Bharat - PMJAY", eligibility_score: 0.75, eligibility_status: "eligible" },
        { id: 3, name: "PM Awas Yojana", eligibility_score: 0.60, eligibility_status: "partial" },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleAskAgain = (question) => {
    navigate("/chat", { state: { prefillQuery: question } });
  };

  const handleExport = async (queryId) => {
    try {
      await reportAPI.downloadQueryPDF(queryId);
      showToast?.("PDF downloaded successfully!", "success");
    } catch {
      showToast?.("Failed to download PDF", "error");
    }
  };

  const greet = () => {
    const h = new Date().getHours();
    if (h < 12) return "🌅 Good Morning";
    if (h < 17) return "☀️ Good Afternoon";
    return "🌙 Good Evening";
  };

  return (
    <div className={styles.dashboard}>
      {/* Header */}
      <div className={styles.dashHeader}>
        <div>
          <h1>{greet()}, {user?.name?.split(" ")[0]} Ji! 🙏</h1>
          <p className="text-muted">
            {new Date().toLocaleDateString("en-IN", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
            {" · "}{user?.state || "India"} · SevaSetu AI Dashboard
          </p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate("/chat")}>
          💬 Ask AI Assistant
        </button>
      </div>

      {/* Stats */}
      <div className={styles.statsGrid}>
        <StatCard
          num={loading ? "..." : stats?.totalQueries ?? 0}
          label="Total Queries"
          icon="💬" color="saffron"
          onClick={() => navigate("/history")}
        />
        <StatCard
          num={loading ? "..." : eligibleSchemes.filter(s => s.eligibility_status === "eligible").length}
          label="Eligible Schemes"
          icon="🏛️" color="green"
          onClick={() => navigate("/schemes")}
        />
        <StatCard
          num="24/7"
          label="AI Available"
          icon="🤖" color="blue"
          onClick={() => navigate("/chat")}
        />
        <StatCard
          num="100+"
          label="Govt. Schemes"
          icon="📋" color="gold"
          onClick={() => navigate("/schemes")}
        />
      </div>

      {/* Quick Actions */}
      <div className={styles.section}>
        <div className={styles.sectionHeader}>
          <h3>⚡ Quick Services</h3>
          <button className="btn btn-ghost btn-sm" onClick={() => navigate("/chat")}>View All →</button>
        </div>
        <div className={styles.quickGrid}>
          {QUICK_ACTIONS.map(({ icon, label, query }) => (
            <button
              key={label}
              className={styles.quickBtn}
              onClick={() => navigate("/chat", { state: { prefillQuery: query } })}
            >
              <span className={styles.quickIcon}>{icon}</span>
              <span className={styles.quickLabel}>{label}</span>
            </button>
          ))}
        </div>
      </div>

      <div className={styles.twoCol}>
        {/* Recent Queries */}
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <h3>🕐 Recent Queries</h3>
            <button className="btn btn-ghost btn-sm" onClick={() => navigate("/history")}>View All →</button>
          </div>
          {loading ? (
            Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="skeleton" style={{ height: 48, marginBottom: 8, borderRadius: 8 }} />
            ))
          ) : recentQueries.length === 0 ? (
            <div className="empty-state" style={{ padding: "30px 0" }}>
              <div className="icon">💬</div>
              <p>No queries yet. Ask something!</p>
              <button className="btn btn-primary btn-sm" onClick={() => navigate("/chat")}>Start Chatting</button>
            </div>
          ) : (
            recentQueries.map((q) => (
              <QueryRow key={q.id} query={q} onAskAgain={handleAskAgain} onExport={handleExport} />
            ))
          )}
        </div>

        {/* Eligible Schemes */}
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <h3>🏛️ Your Eligible Schemes</h3>
            <button className="btn btn-ghost btn-sm" onClick={() => navigate("/schemes")}>Check All →</button>
          </div>
          {loading ? (
            Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="skeleton" style={{ height: 48, marginBottom: 8, borderRadius: 8 }} />
            ))
          ) : eligibleSchemes.length === 0 ? (
            <div className="empty-state" style={{ padding: "30px 0" }}>
              <div className="icon">🏛️</div>
              <p>Complete eligibility check to see matching schemes</p>
              <button className="btn btn-primary btn-sm" onClick={() => navigate("/schemes")}>Check Eligibility</button>
            </div>
          ) : (
            eligibleSchemes.map((s) => <SchemeRow key={s.id} scheme={s} />)
          )}
        </div>
      </div>

      {/* Info banner */}
      <div className={styles.infoBanner}>
        <span className={styles.bannerIcon}>🇮🇳</span>
        <div>
          <strong>SevaSetu AI</strong> — Bridging 1.4 Billion Citizens to Government Services
          <span className={styles.bannerSub}> · Built by Rahul Jha · Made in India · Powered by Gemini AI</span>
        </div>
        <button className="btn btn-secondary btn-sm" onClick={() => navigate("/chat")}>
          Ask AI Now →
        </button>
      </div>
    </div>
  );
}
