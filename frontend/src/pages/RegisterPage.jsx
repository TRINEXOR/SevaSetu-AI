/**
 * SevaSetu AI — Register Page
 * Author: Rahul Jha | Made in India 🇮🇳
 */
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../App";
import { authAPI, getErrorMessage } from "../services/api";
import styles from "./AuthPage.module.css";

const STATES = ["Maharashtra","Delhi","Uttar Pradesh","Bihar","Karnataka","Tamil Nadu","West Bengal","Gujarat","Rajasthan","Madhya Pradesh","Andhra Pradesh","Telangana","Kerala","Punjab","Haryana","Jharkhand","Assam","Odisha","Uttarakhand","Himachal Pradesh","Jammu & Kashmir","Goa","Other"];

export default function RegisterPage() {
  const { login } = useAuth();
  const navigate  = useNavigate();
  const [form, setForm] = useState({ name:"", email:"", mobile:"", password:"", state:"Maharashtra", language:"en" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => { setForm(f => ({ ...f, [e.target.name]: e.target.value })); setError(""); };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.name || !form.email || !form.mobile || !form.password) { setError("All fields required."); return; }
    if (form.password.length < 8) { setError("Password must be at least 8 characters."); return; }
    setLoading(true);
    try {
      const res = await authAPI.register(form);
      login(res.data.user, res.data.access_token, res.data.refresh_token);
      navigate("/dashboard");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally { setLoading(false); }
  };

  return (
    <div className={styles.authPage}>
      <div className={styles.bgParticles}>{Array.from({length:12}).map((_,i)=><div key={i} className={styles.particle} style={{left:`${Math.random()*100}%`,top:`${Math.random()*100}%`,animationDelay:`${Math.random()*5}s`,animationDuration:`${5+Math.random()*8}s`}}/>)}</div>
      <div className={styles.authCard}>
        <div className={styles.tricolorBar}><span style={{background:"#FF6B00"}}/><span style={{background:"#fff"}}/><span style={{background:"#138808"}}/></div>
        <div className={styles.authLogo}><div className={styles.logoText}>SevaSetu AI</div><div className={styles.logoFlag}>🇮🇳</div></div>
        <h1 className={styles.authTitle}>Create Account</h1>
        <p className={styles.authSub}>Create your SevaSetu AI account</p>
        {error && <div className={styles.errorAlert}>⚠️ {error}</div>}
        <form onSubmit={handleSubmit} className={styles.authForm}>
          <div className={styles.twoCol}>
            <div className="form-group"><label className="form-label">Full Name</label><input className="form-input" name="name" value={form.name} onChange={handleChange} placeholder="Your full name" disabled={loading}/></div>
            <div className="form-group"><label className="form-label">Mobile</label><input className="form-input" name="mobile" value={form.mobile} onChange={handleChange} placeholder="9876543210" disabled={loading}/></div>
          </div>
          <div className="form-group"><label className="form-label">Email</label><input className="form-input" type="email" name="email" value={form.email} onChange={handleChange} placeholder="you@example.com" disabled={loading}/></div>
          <div className={styles.twoCol}>
            <div className="form-group"><label className="form-label">State</label><select className="form-select" name="state" value={form.state} onChange={handleChange}>{STATES.map(s=><option key={s}>{s}</option>)}</select></div>
            <div className="form-group"><label className="form-label">Language</label><select className="form-select" name="language" value={form.language} onChange={handleChange}><option value="en">English</option><option value="hi">हिंदी</option><option value="mr">मराठी</option></select></div>
          </div>
          <div className="form-group"><label className="form-label">Password</label><input className="form-input" type="password" name="password" value={form.password} onChange={handleChange} placeholder="Min. 8 characters" disabled={loading}/></div>
          <button type="submit" className="btn btn-primary btn-lg w-full" disabled={loading} style={{marginTop:4}}>
            {loading ? <><div className="spinner sm"/>Creating account...</> : "Create Account 🎉"}
          </button>
        </form>
        <div className={styles.authFooter}><span>Already have an account?</span><Link to="/login" className={styles.authLink}>Sign In →</Link></div>
        <div className={styles.madeIn}>Made with ❤️ in India 🇮🇳 by <strong>Rahul Jha</strong></div>
      </div>
    </div>
  );
}
