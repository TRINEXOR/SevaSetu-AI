/**
 * SevaSetu AI — Main Layout Component
 * Author: Rahul Jha | Made in India 🇮🇳
 *
 * Wraps all authenticated pages with:
 *  - Top navigation bar
 *  - Collapsible sidebar with all routes
 *  - Language switcher
 *  - Profile dropdown
 *  - Toast notifications context
 */

import { useState, useRef, useEffect, createContext, useContext } from "react";
import { Outlet, NavLink, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../App";
import styles from "./MainLayout.module.css";

// ── Toast Context ─────────────────────────────────────────────────────────
export const ToastContext = createContext(null);
export const useToast = () => useContext(ToastContext);

// ── NAV ITEMS ─────────────────────────────────────────────────────────────
const MAIN_NAV = [
  { to: "/dashboard", icon: "📊", label: "Dashboard" },
  { to: "/chat",      icon: "💬", label: "AI Assistant" },
  { to: "/schemes",   icon: "🏛️", label: "Schemes" },
  { to: "/documents", icon: "📄", label: "Documents" },
  { to: "/history",   icon: "📝", label: "History" },
  { to: "/reports",   icon: "📊", label: "Reports" },
];

const SERVICE_NAV = [
  { label: "Voter ID",         icon: "🗳️", query: "How to apply for Voter ID?" },
  { label: "PAN Card",         icon: "💳", query: "PAN card application process?" },
  { label: "Passport",         icon: "📘", query: "Fresh passport application steps?" },
  { label: "Birth Certificate",icon: "📜", query: "Birth certificate online apply?" },
  { label: "Income Cert.",     icon: "📋", query: "How to get income certificate?" },
  { label: "Aadhaar",          icon: "🆔", query: "Aadhaar card update process?" },
];

const LANG_OPTIONS = [
  { value: "en", label: "🇬🇧 English" },
  { value: "hi", label: "🇮🇳 हिंदी" },
  { value: "mr", label: "🟠 मराठी" },
];

// ── Toast Component ───────────────────────────────────────────────────────
function Toast({ toast, onClose }) {
  useEffect(() => {
    const t = setTimeout(() => onClose(toast.id), toast.duration || 3500);
    return () => clearTimeout(t);
  }, [toast]);

  const iconMap = { success: "✅", error: "❌", info: "ℹ️", warning: "⚠️" };
  return (
    <div className={`${styles.toast} ${styles[toast.type || "info"]}`}>
      <span className={styles.toastIcon}>{iconMap[toast.type] || "ℹ️"}</span>
      <span className={styles.toastMsg}>{toast.message}</span>
      <button className={styles.toastClose} onClick={() => onClose(toast.id)}>✕</button>
    </div>
  );
}

// ── Main Layout ───────────────────────────────────────────────────────────
export default function MainLayout() {
  const { user, logout, updateUser } = useAuth();
  const navigate  = useNavigate();
  const location  = useLocation();

  const [sidebarOpen,   setSidebarOpen]   = useState(window.innerWidth > 768);
  const [profileOpen,   setProfileOpen]   = useState(false);
  const [toasts,        setToasts]        = useState([]);
  const [currentLang,   setCurrentLang]   = useState(user?.language || "en");
  const profileRef = useRef(null);

  // Close profile dropdown on outside click
  useEffect(() => {
    const handleClick = (e) => {
      if (profileRef.current && !profileRef.current.contains(e.target)) {
        setProfileOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  // Auto-close sidebar on mobile after navigation
  useEffect(() => {
    if (window.innerWidth <= 768) setSidebarOpen(false);
  }, [location.pathname]);

  // ── Toast API ─────────────────────────────────────────────────────────
  const showToast = (message, type = "info", duration = 3500) => {
    const id = Date.now() + Math.random();
    setToasts((prev) => [...prev, { id, message, type, duration }]);
  };
  const closeToast = (id) => setToasts((prev) => prev.filter((t) => t.id !== id));

  // ── Language change ───────────────────────────────────────────────────
  const handleLangChange = (e) => {
    const lang = e.target.value;
    setCurrentLang(lang);
    updateUser({ language: lang });
    const labels = { en: "English", hi: "हिंदी", mr: "मराठी" };
    showToast(`Language set to ${labels[lang]}`, "success");
  };

  // ── Logout ────────────────────────────────────────────────────────────
  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  // ── Quick service shortcut ─────────────────────────────────────────────
  const handleServiceClick = (query) => {
    navigate("/chat", { state: { prefillQuery: query } });
  };

  // User initials for avatar
  const initials = user?.name
    ? user.name.split(" ").map((n) => n[0]).join("").slice(0, 2).toUpperCase()
    : "?";

  return (
    <ToastContext.Provider value={showToast}>
      <div className={styles.layout}>

        {/* ── Sidebar ────────────────────────────────────────────────── */}
        <aside className={`${styles.sidebar} ${sidebarOpen ? styles.sidebarOpen : styles.sidebarClosed}`}>
          <div className={styles.sidebarInner}>

            {/* Brand */}
            <div className={styles.sidebarBrand}>
              <span className={styles.brandText}>SevaSetu</span>
              <span className={styles.brandAI}> AI</span>
              <span className={styles.brandFlag}>🇮🇳</span>
            </div>

            {/* Main nav */}
            <div className={styles.navSection}>
              <div className={styles.navLabel}>Main</div>
              {MAIN_NAV.map(({ to, icon, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    `${styles.navItem} ${isActive ? styles.navActive : ""}`
                  }
                >
                  <span className={styles.navIcon}>{icon}</span>
                  <span className={styles.navLabel2}>{label}</span>
                </NavLink>
              ))}
            </div>

            {/* Services shortcut */}
            <div className={styles.navSection}>
              <div className={styles.navLabel}>Quick Services</div>
              {SERVICE_NAV.map(({ label, icon, query }) => (
                <button
                  key={label}
                  className={styles.navItem}
                  onClick={() => handleServiceClick(query)}
                >
                  <span className={styles.navIcon}>{icon}</span>
                  <span className={styles.navLabel2}>{label}</span>
                </button>
              ))}
            </div>

            {/* Admin link (admin only) */}
            {user?.role === "admin" && (
              <div className={styles.navSection}>
                <div className={styles.navLabel}>Admin</div>
                <NavLink
                  to="/admin"
                  className={({ isActive }) =>
                    `${styles.navItem} ${isActive ? styles.navActive : ""}`
                  }
                >
                  <span className={styles.navIcon}>⚙️</span>
                  <span className={styles.navLabel2}>Admin Panel</span>
                </NavLink>
              </div>
            )}

            {/* Footer */}
            <div className={styles.sidebarFooter}>
              <div className={styles.footerBrand}>SevaSetu AI v1.0</div>
              <div className={styles.footerAuthor}>
                By <strong style={{ color: "var(--saffron)" }}>Rahul Jha</strong>
              </div>
              <div className={styles.footerMadeIn}>🇮🇳 Made in India</div>
            </div>
          </div>
        </aside>

        {/* Sidebar overlay (mobile) */}
        {sidebarOpen && window.innerWidth <= 768 && (
          <div className={styles.overlay} onClick={() => setSidebarOpen(false)} />
        )}

        {/* ── Main Area ──────────────────────────────────────────────── */}
        <div className={styles.mainArea}>

          {/* Top Nav */}
          <header className={styles.topnav}>
            <button
              className={styles.menuBtn}
              onClick={() => setSidebarOpen((o) => !o)}
              aria-label="Toggle sidebar"
            >
              ☰
            </button>

            <div className={styles.navBrand} onClick={() => navigate("/dashboard")}>
              <span className={styles.navBrandText}>SevaSetu AI</span>
              <span className={styles.navBrandFlag}>🇮🇳</span>
            </div>

            <div className={styles.navSpacer} />

            {/* Language selector */}
            <select
              className={styles.langSelect}
              value={currentLang}
              onChange={handleLangChange}
            >
              {LANG_OPTIONS.map((l) => (
                <option key={l.value} value={l.value}>{l.label}</option>
              ))}
            </select>

            {/* Chat shortcut */}
            <button
              className={`${styles.navActionBtn} ${location.pathname === "/chat" ? styles.navActionActive : ""}`}
              onClick={() => navigate("/chat")}
            >
              💬 Chat
            </button>

            {/* Profile */}
            <div className={styles.profileWrap} ref={profileRef}>
              <button
                className={styles.avatarBtn}
                onClick={() => setProfileOpen((o) => !o)}
                aria-label="Profile menu"
              >
                {initials}
              </button>

              {profileOpen && (
                <div className={styles.profileDropdown}>
                  <div className={styles.profileHeader}>
                    <div className={styles.profileName}>{user?.name}</div>
                    <div className={styles.profileEmail}>{user?.email}</div>
                    <div className={`badge badge-${user?.role === "admin" ? "saffron" : "blue"}`}>
                      {user?.role?.toUpperCase()}
                    </div>
                  </div>
                  <div className={styles.dropdownDivider} />
                  {[
                    { to: "/dashboard", icon: "📊", label: "Dashboard" },
                    { to: "/profile",   icon: "👤", label: "My Profile" },
                    { to: "/history",   icon: "📝", label: "Query History" },
                    { to: "/reports",   icon: "📊", label: "Reports" },
                  ].map(({ to, icon, label }) => (
                    <button
                      key={to}
                      className={styles.dropdownItem}
                      onClick={() => { navigate(to); setProfileOpen(false); }}
                    >
                      <span>{icon}</span> {label}
                    </button>
                  ))}
                  <div className={styles.dropdownDivider} />
                  <button
                    className={`${styles.dropdownItem} ${styles.dropdownDanger}`}
                    onClick={handleLogout}
                  >
                    <span>🚪</span> Logout
                  </button>
                </div>
              )}
            </div>
          </header>

          {/* Page Content */}
          <main className={styles.pageContent}>
            <Outlet />
          </main>
        </div>
      </div>

      {/* Toast Container */}
      <div className={styles.toastContainer}>
        {toasts.map((t) => (
          <Toast key={t.id} toast={t} onClose={closeToast} />
        ))}
      </div>
    </ToastContext.Provider>
  );
}
