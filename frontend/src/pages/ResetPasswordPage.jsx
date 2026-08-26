import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { authAPI, getErrorMessage } from "../services/api";
import styles from "./AuthPage.module.css";

export default function ResetPasswordPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const token = params.get("token") || "";
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    if (!token) { setError("This password reset link is invalid or incomplete."); return; }
    if (password.length < 8) { setError("Password must be at least 8 characters."); return; }
    if (!/[A-Z]/.test(password) || !/\d/.test(password)) { setError("Password must contain at least one uppercase letter and one digit."); return; }
    if (password !== confirm) { setError("Passwords do not match."); return; }
    setLoading(true);
    try {
      await authAPI.resetPassword(token, password);
      setSuccess("Your password has been reset successfully. You can now sign in.");
      setTimeout(() => navigate("/login"), 1200);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally { setLoading(false); }
  };

  return (
    <div className={styles.authPage}>
      <div className={styles.authCard}>
        <div className={styles.tricolorBar}><span style={{background:"#FF6B00"}}/><span style={{background:"#fff"}}/><span style={{background:"#138808"}}/></div>
        <div className={styles.authLogo}><div className={styles.logoText}>SevaSetu AI</div><div className={styles.logoFlag}>🇮🇳</div></div>
        <h1 className={styles.authTitle}>Set New Password</h1>
        <p className={styles.authSub}>Choose a strong password for your account.</p>
        {error && <div className={styles.errorAlert}>⚠️ {error}</div>}
        {success && <div className={styles.successAlert}>✅ {success}</div>}
        <form onSubmit={submit} className={styles.authForm}>
          <div className="form-group"><label className="form-label">New Password</label><input className="form-input" type="password" value={password} onChange={(e)=>setPassword(e.target.value)} placeholder="Min. 8 characters" autoComplete="new-password" disabled={loading}/></div>
          <div className="form-group"><label className="form-label">Confirm Password</label><input className="form-input" type="password" value={confirm} onChange={(e)=>setConfirm(e.target.value)} placeholder="Re-enter password" autoComplete="new-password" disabled={loading}/></div>
          <button type="submit" className="btn btn-primary btn-lg w-full" disabled={loading || !!success}>
            {loading ? <><div className="spinner sm"/> Resetting...</> : "Reset Password 🔐"}
          </button>
        </form>
        <div className={styles.authFooter}><Link to="/login" className={styles.authLink}>← Back to Sign In</Link></div>
      </div>
    </div>
  );
}
