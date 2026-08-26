/**
 * SevaSetu AI — Login Page
 * Author: Rahul Jha | Made in India 🇮🇳
 *
 */

import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../App";
import { authAPI, getErrorMessage } from "../services/api";
import styles from "./AuthPage.module.css";

export default function LoginPage() {
  const { login }  = useAuth();
  const navigate   = useNavigate();

  const [form,     setForm]     = useState({ email: "", password: "" });
  const [error,    setError]    = useState("");
  const [loading,  setLoading]  = useState(false);
  const [showPass, setShowPass] = useState(false);

  const handleChange = (e) => {
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
    setError("");
  };

  // ── Real login (requires backend) ─────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.email || !form.password) {
      setError("Please enter your email and password.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const res  = await authAPI.login(form.email, form.password);
      const data = res.data;
      login(data.user, data.access_token, data.refresh_token);
      navigate("/dashboard");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };



  return (
    <div className={styles.authPage}>
      {/* Background particles */}
      <div className={styles.bgParticles}>
        {Array.from({ length: 20 }).map((_, i) => (
          <div key={i} className={styles.particle} style={{
            left:              `${Math.random() * 100}%`,
            top:               `${Math.random() * 100}%`,
            animationDelay:    `${Math.random() * 5}s`,
            animationDuration: `${5 + Math.random() * 8}s`,
            width:             `${3 + Math.random() * 5}px`,
            height:            `${3 + Math.random() * 5}px`,
          }} />
        ))}
      </div>

      <div className={styles.authCard}>
        {/* Tricolor top bar */}
        <div className={styles.tricolorBar}>
          <span style={{ background: "#FF6B00" }} />
          <span style={{ background: "#fff" }} />
          <span style={{ background: "#138808" }} />
        </div>

        {/* Logo */}
        <div className={styles.authLogo}>
          <div className={styles.logoText}>SevaSetu AI</div>
          <div className={styles.logoFlag}>🇮🇳</div>
        </div>

        <h1 className={styles.authTitle}>Welcome Back</h1>
        <p className={styles.authSub}>Sign in to access government services</p>

        {error && <div className={styles.errorAlert}>⚠️ {error}</div>}

        {/* ── Sign-in form ─────────────────────────────────────────── */}
        <form onSubmit={handleSubmit} className={styles.authForm}>
          <div className="form-group">
            <label className="form-label">Email / Mobile</label>
            <input
              className="form-input"
              type="text"
              name="email"
              value={form.email}
              onChange={handleChange}
              placeholder="Enter email or mobile number"
              autoComplete="username"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label className="form-label">
              Password
              <Link to="/forgot-password" className={styles.forgotLink}>Forgot password?</Link>
            </label>
            <div className={styles.passwordWrap}>
              <input
                className="form-input"
                type={showPass ? "text" : "password"}
                name="password"
                value={form.password}
                onChange={handleChange}
                placeholder="Enter your password"
                autoComplete="current-password"
                disabled={loading}
              />
              <button
                type="button"
                className={styles.eyeBtn}
                onClick={() => setShowPass((v) => !v)}
              >
                {showPass ? "🙈" : "👁️"}
              </button>
            </div>
          </div>

          <button
            type="submit"
            className={`btn btn-primary btn-lg w-full ${styles.submitBtn}`}
            disabled={loading}
          >
            {loading ? (
              <><div className="spinner sm" /> Signing in...</>
            ) : (
              "Sign In 🔐"
            )}
          </button>
        </form>

        {/* ── Footer ──────────────────────────────────────────────────── */}
        <div className={styles.authFooter} style={{ marginTop: 16 }}>
          <span>New to SevaSetu AI?</span>
          <Link to="/register" className={styles.authLink}>Create Account →</Link>
        </div>

        <div className={styles.madeIn}>
          Made with ❤️ in India 🇮🇳 by <strong>Rahul Jha</strong>
        </div>
      </div>
    </div>
  );
}
