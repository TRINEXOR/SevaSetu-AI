/**
 * SevaSetu AI — React Frontend Root App
 * Author: Rahul Jha | Made in India 🇮🇳
 *
 * Routing structure:
 *   /         → Splash → Login/Register → Dashboard
 *   /login    → Login page
 *   /register → Register page
 *   /dashboard→ User dashboard
 *   /chat     → AI Chat interface
 *   /schemes  → Government schemes browser
 *   /documents→ Document upload & checklist
 *   /history  → Query history
 *   /reports  → PDF reports
 *   /admin    → Admin panel (admin role only)
 *   /profile  → User profile settings
 */

import { useState, useEffect, createContext, useContext } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import "./App.css";

// ── Pages ──────────────────────────────────────────────────────────────────
import SplashScreen  from "./pages/SplashScreen";
import LoginPage     from "./pages/LoginPage";
import RegisterPage  from "./pages/RegisterPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import ResetPasswordPage  from "./pages/ResetPasswordPage";
import Dashboard     from "./pages/Dashboard";
import ChatPage      from "./pages/ChatPage";
import SchemesPage   from "./pages/SchemesPage";
import DocumentsPage from "./pages/DocumentsPage";
import HistoryPage   from "./pages/HistoryPage";
import AdminPage     from "./pages/AdminPage";
import ProfilePage   from "./pages/ProfilePage";
import ReportsPage   from "./pages/ReportsPage";

// ── Components ─────────────────────────────────────────────────────────────
import MainLayout    from "./components/MainLayout";
import LoadingSpinner from "./components/LoadingSpinner";

// ── Auth Context ───────────────────────────────────────────────────────────
export const AuthContext = createContext(null);

export function useAuth() {
  return useContext(AuthContext);
}

// ── Auth Provider ──────────────────────────────────────────────────────────
function AuthProvider({ children }) {
  const [user, setUser]       = useState(null);
  const [token, setToken]     = useState(localStorage.getItem("ss_token"));
  const [loading, setLoading] = useState(true);

  // Validate token on mount
  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem("ss_token");
      if (!savedToken) { setLoading(false); return; }

      try {
        const apiBase = (process.env.REACT_APP_API_URL || window.location.origin).replace(/\/$/, "").replace(/\/api\/v1$/, "");
        const res = await fetch(`${apiBase}/api/v1/auth/me`, {
          headers: { Authorization: `Bearer ${savedToken}` },
        });
        if (res.ok) {
          const data = await res.json();
          setUser(data);
          setToken(savedToken);
        } else {
          // Token expired / invalid
          localStorage.removeItem("ss_token");
          localStorage.removeItem("ss_refresh");
          setUser(null);
          setToken(null);
        }
      } catch {
        // Network error — keep user logged in from localStorage
        const savedUser = localStorage.getItem("ss_user");
        if (savedUser) setUser(JSON.parse(savedUser));
      } finally {
        setLoading(false);
      }
    };
    initAuth();
  }, []);

  const login = (userData, accessToken, refreshToken) => {
    setUser(userData);
    setToken(accessToken);
    localStorage.setItem("ss_token",   accessToken);
    localStorage.setItem("ss_refresh", refreshToken);
    localStorage.setItem("ss_user",    JSON.stringify(userData));
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("ss_token");
    localStorage.removeItem("ss_refresh");
    localStorage.removeItem("ss_user");
  };

  const updateUser = (newData) => {
    const updated = { ...user, ...newData };
    setUser(updated);
    localStorage.setItem("ss_user", JSON.stringify(updated));
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, updateUser, loading }}>
      {children}
    </AuthContext.Provider>
  );
}

// ── Protected Route ────────────────────────────────────────────────────────
function ProtectedRoute({ children, adminOnly = false }) {
  const { user, loading } = useAuth();

  if (loading) return <LoadingSpinner fullscreen />;
  if (!user)   return <Navigate to="/login" replace />;
  if (adminOnly && user.role !== "admin") return <Navigate to="/dashboard" replace />;
  return children;
}

// ── App Routes ─────────────────────────────────────────────────────────────
function AppRoutes() {
  const { user } = useAuth();
  const [splashDone, setSplashDone] = useState(
    sessionStorage.getItem("splash_shown") === "true"
  );

  const handleSplashComplete = () => {
    sessionStorage.setItem("splash_shown", "true");
    setSplashDone(true);
  };

  // Show splash only once per session
  if (!splashDone) {
    return <SplashScreen onComplete={handleSplashComplete} />;
  }

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login"    element={user ? <Navigate to="/dashboard" /> : <LoginPage />} />
      <Route path="/register" element={user ? <Navigate to="/dashboard" /> : <RegisterPage />} />
      <Route path="/forgot-password" element={user ? <Navigate to="/dashboard" /> : <ForgotPasswordPage />} />
      <Route path="/reset-password" element={user ? <Navigate to="/dashboard" /> : <ResetPasswordPage />} />

      {/* Protected routes — all wrapped in MainLayout */}
      <Route path="/" element={
        <ProtectedRoute>
          <MainLayout />
        </ProtectedRoute>
      }>
        <Route index            element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="chat"      element={<ChatPage />} />
        <Route path="schemes"   element={<SchemesPage />} />
        <Route path="documents" element={<DocumentsPage />} />
        <Route path="history"   element={<HistoryPage />} />
        <Route path="reports"   element={<ReportsPage />} />
        <Route path="profile"   element={<ProfilePage />} />
        <Route path="admin"     element={
          <ProtectedRoute adminOnly>
            <AdminPage />
          </ProtectedRoute>
        } />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<Navigate to={user ? "/dashboard" : "/login"} replace />} />
    </Routes>
  );
}

// ── Root App ───────────────────────────────────────────────────────────────
export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
