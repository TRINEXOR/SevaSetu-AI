import { useState } from "react";
import { Link } from "react-router-dom";
import { authAPI, getErrorMessage } from "../services/api";
import styles from "./AuthPage.module.css";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    if (!email.trim()) {
      setError("Please enter your registered email address.");
      return;
    }
    setLoading(true);
    try {
      await authAPI.forgotPassword(email.trim());
      setSuccess("If an account exists for this email, a password reset link has been sent. Please check your inbox.");
      setEmail("");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.authPage}>
      <div className={styles.authCard}>
        <div className={styles.tricolorBar}><span style={{background:"#FF6B00"}}/><span style={{background:"#fff"}}/><span style={{background:"#138808"}}/></div>
        <div className={styles.authLogo}><div className={styles.logoText}>SevaSetu AI</div><div className={styles.logoFlag}>🇮🇳</div></div>
        <h1 className={styles.authTitle}>Forgot Password?</h1>
        <p className={styles.authSub}>Enter your registered email to receive a secure reset link.</p>
        {error && <div className={styles.errorAlert}>⚠️ {error}</div>}
        {success && <div className={styles.successAlert}>✅ {success}</div>}
        <form onSubmit={submit} className={styles.authForm}>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input className="form-input" type="email" value={email} onChange={(e)=>setEmail(e.target.value)} placeholder="you@example.com" autoComplete="email" disabled={loading}/>
          </div>
          <button type="submit" className="btn btn-primary btn-lg w-full" disabled={loading}>
            {loading ? <><div className="spinner sm"/> Sending link...</> : "Send Reset Link ✉️"}
          </button>
        </form>
        <div className={styles.authFooter}>
          <Link to="/login" className={styles.authLink}>← Back to Sign In</Link>
        </div>
        <div className={styles.madeIn}>Made with ❤️ in India 🇮🇳 by <strong>Rahul Jha</strong></div>
      </div>
    </div>
  );
}
