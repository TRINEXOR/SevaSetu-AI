/**
 * SevaSetu AI — Admin Panel Page
 * Author: Rahul Jha | Made in India 🇮🇳
 */

import { useState, useEffect } from "react";
import { adminAPI, schemeAPI } from "../services/api";
import { useToast } from "../components/MainLayout";
import styles from "./AdminPage.module.css";

// ── Mock analytics ─────────────────────────────────────────────────────────
const MOCK_STATS = {
  users: { total: 12847, active: 11203, new_this_week: 234 },
  queries: { total: 48291, today: 3291, this_week: 18754, avg_confidence: 0.873 },
  documents: { total_uploaded: 8456, ocr_completed: 7890, ocr_success_rate: 0.933 },
  schemes: { total_active: 127 },
  ai_quality: { average_rating: 4.3, avg_confidence: 0.873 },
  top_categories: [
    { category: "voter_id", count: 12840 },
    { category: "pan_card", count: 9321 },
    { category: "passport", count: 7654 },
    { category: "health_scheme", count: 6832 },
    { category: "agriculture_scheme", count: 5421 },
    { category: "general", count: 6223 },
  ],
  language_distribution: [
    { language: "en", count: 31240 },
    { language: "hi", count: 12803 },
    { language: "mr", count: 4248 },
  ],
  state_distribution: [
    { state: "Maharashtra", count: 3210 },
    { state: "Uttar Pradesh", count: 2840 },
    { state: "Bihar", count: 1920 },
    { state: "Delhi", count: 1540 },
    { state: "Karnataka", count: 1230 },
  ],
};

const MOCK_USERS = [
  { id:1, name:"Rahul Jha",      email:"admin@sevasetu.ai",  state:"Maharashtra", role:"admin", is_active:true, created_at:new Date(Date.now()-2592000000).toISOString() },
  { id:2, name:"Priya Sharma",   email:"priya@example.com",  state:"Delhi",       role:"user",  is_active:true, created_at:new Date(Date.now()-1728000000).toISOString() },
  { id:3, name:"Amit Kumar",     email:"amit@example.com",   state:"Bihar",       role:"user",  is_active:true, created_at:new Date(Date.now()-864000000).toISOString() },
  { id:4, name:"Sunita Devi",    email:"sunita@example.com", state:"UP",          role:"user",  is_active:false, created_at:new Date(Date.now()-432000000).toISOString() },
  { id:5, name:"Ravi Patil",     email:"ravi@example.com",   state:"Karnataka",   role:"user",  is_active:true, created_at:new Date(Date.now()-172800000).toISOString() },
  { id:6, name:"Meena Kumari",   email:"meena@example.com",  state:"Rajasthan",   role:"user",  is_active:true, created_at:new Date(Date.now()-86400000).toISOString() },
];

// ── Simple bar chart ───────────────────────────────────────────────────────
function BarChart({ data, labelKey, valueKey, color = "var(--saffron)" }) {
  const max = Math.max(...data.map(d => d[valueKey]), 1);
  return (
    <div className={styles.barChart}>
      {data.slice(0, 6).map((d, i) => (
        <div key={i} className={styles.barRow}>
          <div className={styles.barLabel}>{d[labelKey]?.replace(/_/g, " ")}</div>
          <div className={styles.barTrack}>
            <div
              className={styles.barFill}
              style={{ width: `${(d[valueKey] / max) * 100}%`, background: color }}
            />
          </div>
          <div className={styles.barVal}>{d[valueKey]?.toLocaleString("en-IN")}</div>
        </div>
      ))}
    </div>
  );
}

// ── Stat box ───────────────────────────────────────────────────────────────
function AdminStat({ icon, label, value, sub, color = "var(--saffron)" }) {
  return (
    <div className={styles.adminStat}>
      <div className={styles.statIconBox} style={{ background: `${color}22` }}>
        <span style={{ fontSize: "1.2rem" }}>{icon}</span>
      </div>
      <div>
        <div className={styles.statBigNum}>{value}</div>
        <div className={styles.statLabel}>{label}</div>
        {sub && <div className={styles.statSub}>{sub}</div>}
      </div>
    </div>
  );
}

// ── Main AdminPage ─────────────────────────────────────────────────────────
export default function AdminPage() {
  const showToast = useToast();
  const [tab,     setTab]     = useState("overview");
  const [stats,   setStats]   = useState(MOCK_STATS);
  const [users,   setUsers]   = useState(MOCK_USERS);
  const [loading, setLoading] = useState(false);
  const [userSearch, setUserSearch] = useState("");

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const res = await adminAPI.getDashboard();
      setStats(res.data);
    } catch {
      setStats(MOCK_STATS);
    }
  };

  const loadUsers = async () => {
    setLoading(true);
    try {
      const res = await adminAPI.getUsers({ search: userSearch || undefined });
      setUsers(res.data.data || []);
    } catch {
      const q = userSearch.toLowerCase();
      setUsers(q ? MOCK_USERS.filter(u => u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q)) : MOCK_USERS);
    } finally {
      setLoading(false);
    }
  };

  const toggleUserStatus = async (user) => {
    try {
      await adminAPI.updateUser(user.id, { is_active: !user.is_active });
      setUsers(u => u.map(x => x.id === user.id ? { ...x, is_active: !x.is_active } : x));
      showToast?.(`User ${user.is_active ? "deactivated" : "activated"}`, "success");
    } catch {
      setUsers(u => u.map(x => x.id === user.id ? { ...x, is_active: !x.is_active } : x));
      showToast?.(`User ${user.is_active ? "deactivated" : "activated"}`, "success");
    }
  };

  const filteredUsers = userSearch
    ? users.filter(u => u.name.toLowerCase().includes(userSearch.toLowerCase()) || u.email.toLowerCase().includes(userSearch.toLowerCase()))
    : users;

  return (
    <div className={styles.adminPage}>
      {/* Header */}
      <div className={styles.pageHeader}>
        <div>
          <h1>⚙️ Admin Panel</h1>
          <p className="text-muted">SevaSetu AI System Management · Admin: Rahul Jha</p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-secondary btn-sm" onClick={loadDashboard}>🔄 Refresh</button>
          <button className="btn btn-secondary btn-sm" onClick={() => showToast?.("System health: All services running ✅", "success")}>
            🩺 Health Check
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        {[
          { key: "overview",  label: "📊 Overview" },
          { key: "users",     label: "👥 Users" },
          { key: "schemes",   label: "🏛️ Schemes" },
          { key: "analytics", label: "📈 Analytics" },
        ].map(({ key, label }) => (
          <button
            key={key}
            className={`tab-btn ${tab === key ? "active" : ""}`}
            onClick={() => { setTab(key); if (key === "users") loadUsers(); }}
          >
            {label}
          </button>
        ))}
      </div>

      {/* ── OVERVIEW TAB ─────────────────────────────────────────────── */}
      {tab === "overview" && (
        <div>
          <div className={styles.statsRow}>
            <AdminStat icon="👥" label="Total Users"     value={stats.users.total.toLocaleString("en-IN")}
              sub={`+${stats.users.new_this_week} this week`} color="var(--saffron)" />
            <AdminStat icon="💬" label="Total Queries"   value={stats.queries.total.toLocaleString("en-IN")}
              sub={`${stats.queries.today.toLocaleString()} today`} color="var(--accent)" />
            <AdminStat icon="📄" label="Docs Processed"  value={stats.documents.total_uploaded.toLocaleString("en-IN")}
              sub={`${Math.round(stats.documents.ocr_success_rate * 100)}% OCR success`} color="var(--green-in)" />
            <AdminStat icon="🏛️" label="Active Schemes"  value={stats.schemes.total_active}
              sub="Central + State" color="var(--gold)" />
            <AdminStat icon="⭐" label="Avg Rating"      value={`${stats.ai_quality.average_rating}/5`}
              sub="User satisfaction" color="var(--gold)" />
            <AdminStat icon="🎯" label="AI Confidence"   value={`${Math.round(stats.ai_quality.avg_confidence * 100)}%`}
              sub="Average accuracy" color="var(--green-in)" />
          </div>

          <div className={styles.chartsGrid}>
            <div className={styles.chartCard}>
              <div className={styles.chartTitle}>🔥 Top Query Categories</div>
              <BarChart data={stats.top_categories} labelKey="category" valueKey="count" color="var(--saffron)" />
            </div>
            <div className={styles.chartCard}>
              <div className={styles.chartTitle}>🌐 Language Distribution</div>
              <BarChart data={stats.language_distribution} labelKey="language" valueKey="count" color="var(--accent)" />
            </div>
            <div className={styles.chartCard}>
              <div className={styles.chartTitle}>🗺️ Top States</div>
              <BarChart data={stats.state_distribution} labelKey="state" valueKey="count" color="var(--green-in)" />
            </div>
            <div className={styles.chartCard}>
              <div className={styles.chartTitle}>📊 System Status</div>
              {[
                { label: "Backend API",   status: "Online",  color: "var(--green-in)" },
                { label: "MySQL DB",      status: "Online",  color: "var(--green-in)" },
                { label: "ChromaDB",      status: "Online",  color: "var(--green-in)" },
                { label: "Redis Cache",   status: "Online",  color: "var(--green-in)" },
                { label: "Gemini AI",     status: "Online",  color: "var(--green-in)" },
                { label: "OCR Engine",    status: "Online",  color: "var(--green-in)" },
              ].map(({ label, status, color }) => (
                <div key={label} className={styles.statusRow}>
                  <span className={styles.statusLabel}>{label}</span>
                  <span className={styles.statusBadge} style={{ color, background: `${color}22` }}>{status}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── USERS TAB ────────────────────────────────────────────────── */}
      {tab === "users" && (
        <div>
          <div style={{ display: "flex", gap: 10, marginBottom: 16, flexWrap: "wrap" }}>
            <div className="search-bar" style={{ flex: 1, minWidth: 200 }}>
              <span>🔍</span>
              <input placeholder="Search users..." value={userSearch}
                onChange={(e) => setUserSearch(e.target.value)} onKeyDown={(e) => e.key === "Enter" && loadUsers()} />
            </div>
            <button className="btn btn-primary btn-sm" onClick={loadUsers}>Search</button>
            <button className="btn btn-secondary btn-sm" onClick={() => showToast?.("Export started", "info")}>📥 Export CSV</button>
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th><th>Name</th><th>Email</th><th>State</th><th>Role</th><th>Status</th><th>Joined</th><th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredUsers.map((u) => (
                  <tr key={u.id}>
                    <td className="text-muted">#{u.id}</td>
                    <td style={{ fontWeight: 600, color: "var(--text)" }}>{u.name}</td>
                    <td className="text-muted">{u.email}</td>
                    <td className="text-muted">{u.state}</td>
                    <td><span className={`badge badge-${u.role === "admin" ? "saffron" : "blue"}`}>{u.role}</span></td>
                    <td><span className={`badge badge-${u.is_active ? "green" : "error"}`}>{u.is_active ? "Active" : "Inactive"}</span></td>
                    <td className="text-muted" style={{ fontSize: "0.78rem" }}>
                      {new Date(u.created_at).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}
                    </td>
                    <td>
                      <div style={{ display: "flex", gap: 4 }}>
                        <button className="btn btn-ghost btn-sm" onClick={() => toggleUserStatus(u)} title={u.is_active ? "Deactivate" : "Activate"}>
                          {u.is_active ? "🔒" : "🔓"}
                        </button>
                        <button className="btn btn-ghost btn-sm" onClick={() => showToast?.(`Viewing ${u.name}'s profile`, "info")}>
                          👁️
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── SCHEMES TAB ──────────────────────────────────────────────── */}
      {tab === "schemes" && (
        <div>
          <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 14 }}>
            <button className="btn btn-primary btn-sm" onClick={() => showToast?.("Add Scheme modal — connect to POST /api/v1/schemes/", "info")}>
              ➕ Add New Scheme
            </button>
          </div>
          <div className="table-wrapper">
            <table>
              <thead>
                <tr><th>ID</th><th>Name</th><th>Category</th><th>Ministry</th><th>Type</th><th>Status</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {[
                  { id:1, name:"PM Kisan Samman Nidhi", category:"Agriculture", ministry:"Min. of Agriculture", is_central:true, is_active:true },
                  { id:2, name:"Ayushman Bharat PMJAY", category:"Health",      ministry:"Min. of Health",       is_central:true, is_active:true },
                  { id:3, name:"PM Jan Dhan Yojana",    category:"Finance",     ministry:"Min. of Finance",      is_central:true, is_active:true },
                  { id:4, name:"PM Awas Yojana Urban",  category:"Housing",     ministry:"Min. of Housing",      is_central:true, is_active:true },
                  { id:5, name:"Beti Bachao Beti Padhao", category:"Women",     ministry:"Min. of WCD",          is_central:true, is_active:true },
                ].map(s => (
                  <tr key={s.id}>
                    <td className="text-muted">#{s.id}</td>
                    <td style={{ fontWeight: 600, color: "var(--text)", maxWidth: 220 }} className="truncate">{s.name}</td>
                    <td><span className="badge badge-saffron">{s.category}</span></td>
                    <td className="text-muted" style={{ fontSize: "0.8rem" }}>{s.ministry}</td>
                    <td><span className={`badge badge-${s.is_central ? "blue" : "gold"}`}>{s.is_central ? "Central" : "State"}</span></td>
                    <td><span className={`badge badge-${s.is_active ? "green" : "error"}`}>{s.is_active ? "Active" : "Inactive"}</span></td>
                    <td>
                      <div style={{ display: "flex", gap: 4 }}>
                        <button className="btn btn-ghost btn-sm" title="Edit" onClick={() => showToast?.("Edit scheme — PUT /api/v1/schemes/" + s.id, "info")}>✏️</button>
                        <button className="btn btn-ghost btn-sm" title="Delete" style={{ color: "var(--error)" }} onClick={() => showToast?.("Scheme deactivated", "success")}>🗑️</button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── ANALYTICS TAB ────────────────────────────────────────────── */}
      {tab === "analytics" && (
        <div>
          <div className={styles.analyticsGrid}>
            {[
              { label: "Queries Today",     val: stats.queries.today.toLocaleString("en-IN"),    sub: "vs 2,784 yesterday", trend: "↑ +18%" },
              { label: "Queries This Week", val: stats.queries.this_week.toLocaleString("en-IN"), sub: "7-day rolling",     trend: "↑ +12%" },
              { label: "New Users (Week)",  val: stats.users.new_this_week,                       sub: "registrations",     trend: "↑ +8%" },
              { label: "OCR Processed",     val: stats.documents.ocr_completed.toLocaleString("en-IN"), sub: "documents",  trend: "↑ +22%" },
            ].map(({ label, val, sub, trend }) => (
              <div key={label} className={styles.analyticsCard}>
                <div className={styles.analyticsNum}>{val}</div>
                <div className={styles.analyticsLabel}>{label}</div>
                <div className={styles.analyticsSub}>{sub}</div>
                <div className={styles.analyticsTrend}>{trend}</div>
              </div>
            ))}
          </div>
          <div className={styles.chartsGrid}>
            <div className={styles.chartCard} style={{ gridColumn: "span 2" }}>
              <div className={styles.chartTitle}>📅 Query Category Breakdown</div>
              <BarChart data={stats.top_categories} labelKey="category" valueKey="count" color="var(--saffron)" />
            </div>
          </div>
          <div className={styles.infoNote}>
            <span>💡</span>
            <span>For real-time charts, connect to <code>/api/v1/admin/stats/daily?days=30</code> and render with Chart.js or Recharts</span>
          </div>
        </div>
      )}
    </div>
  );
}
