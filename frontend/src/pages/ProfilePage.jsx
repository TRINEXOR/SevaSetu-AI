/**
 * SevaSetu AI — Profile Page
 * Author: Rahul Jha | Made in India 🇮🇳
 */
import { useState } from "react";
import { useAuth } from "../App";
import { useToast } from "../components/MainLayout";
import { authAPI } from "../services/api";

const STATES = ["Maharashtra","Delhi","Uttar Pradesh","Bihar","Karnataka","Tamil Nadu","West Bengal","Gujarat","Rajasthan","Madhya Pradesh","Other"];

export default function ProfilePage() {
  const { user, updateUser } = useAuth();
  const showToast = useToast();
  const [form, setForm] = useState({ name: user?.name||"", email: user?.email||"", mobile: user?.mobile||"", state: user?.state||"Maharashtra", language: user?.language||"en" });
  const [pwForm, setPwForm] = useState({ current_password:"", new_password:"" });
  const [saving, setSaving] = useState(false);
  const [savingPw, setSavingPw] = useState(false);

  const handleSave = async (e) => {
    e.preventDefault(); setSaving(true);
    try { updateUser(form); showToast?.("Profile updated!", "success"); } catch { showToast?.("Update failed", "error"); } finally { setSaving(false); }
  };

  const handlePwChange = async (e) => {
    e.preventDefault(); setSavingPw(true);
    try {
      await authAPI.changePassword(pwForm);
      showToast?.("Password changed successfully!", "success");
      setPwForm({ current_password:"", new_password:"" });
    } catch { showToast?.("Password change failed", "error"); } finally { setSavingPw(false); }
  };

  const initials = user?.name?.split(" ").map(n=>n[0]).join("").slice(0,2).toUpperCase() || "?";

  return (
    <div style={{ padding:20, height:"100%", overflowY:"auto", maxWidth:700, margin:"0 auto" }}>
      <h1 style={{ color:"var(--text)", marginBottom:4 }}>👤 My Profile</h1>
      <p className="text-muted" style={{ marginBottom:24 }}>Manage your SevaSetu AI account</p>

      {/* Avatar */}
      <div style={{ display:"flex", alignItems:"center", gap:18, marginBottom:24, background:"var(--surface)", border:"1px solid var(--border)", borderRadius:"var(--radius-xl)", padding:20 }}>
        <div style={{ width:72, height:72, borderRadius:"50%", background:"linear-gradient(135deg,var(--saffron),var(--gold))", display:"flex", alignItems:"center", justifyContent:"center", fontSize:"1.6rem", fontWeight:800, color:"#fff", flexShrink:0 }}>{initials}</div>
        <div>
          <div style={{ fontSize:"1.1rem", fontWeight:700, color:"var(--text)" }}>{user?.name}</div>
          <div style={{ fontSize:"0.85rem", color:"var(--text-2)" }}>{user?.email}</div>
          <div style={{ marginTop:6, display:"flex", gap:6 }}>
            <span className={`badge badge-${user?.role==="admin"?"saffron":"blue"}`}>{user?.role?.toUpperCase()}</span>
            <span className="badge badge-green">Active</span>
          </div>
        </div>
      </div>

      {/* Profile form */}
      <div style={{ background:"var(--surface)", border:"1px solid var(--border)", borderRadius:"var(--radius-lg)", padding:20, marginBottom:16 }}>
        <h3 style={{ color:"var(--text)", marginBottom:16 }}>Personal Information</h3>
        <form onSubmit={handleSave}>
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:12 }}>
            <div className="form-group"><label className="form-label">Full Name</label><input className="form-input" value={form.name} onChange={e=>setForm(f=>({...f,name:e.target.value}))} /></div>
            <div className="form-group"><label className="form-label">Mobile</label><input className="form-input" value={form.mobile} onChange={e=>setForm(f=>({...f,mobile:e.target.value}))} /></div>
            <div className="form-group"><label className="form-label">Email</label><input className="form-input" type="email" value={form.email} onChange={e=>setForm(f=>({...f,email:e.target.value}))} /></div>
            <div className="form-group"><label className="form-label">State</label><select className="form-select" value={form.state} onChange={e=>setForm(f=>({...f,state:e.target.value}))}>{STATES.map(s=><option key={s}>{s}</option>)}</select></div>
            <div className="form-group"><label className="form-label">Preferred Language</label><select className="form-select" value={form.language} onChange={e=>setForm(f=>({...f,language:e.target.value}))}><option value="en">English</option><option value="hi">हिंदी</option><option value="mr">मराठी</option></select></div>
          </div>
          <button type="submit" className="btn btn-primary" disabled={saving}>{saving?"Saving...":"Save Changes"}</button>
        </form>
      </div>

      {/* Password form */}
      <div style={{ background:"var(--surface)", border:"1px solid var(--border)", borderRadius:"var(--radius-lg)", padding:20 }}>
        <h3 style={{ color:"var(--text)", marginBottom:16 }}>🔒 Change Password</h3>
        <form onSubmit={handlePwChange}>
          <div className="form-group"><label className="form-label">Current Password</label><input className="form-input" type="password" value={pwForm.current_password} onChange={e=>setPwForm(f=>({...f,current_password:e.target.value}))} /></div>
          <div className="form-group"><label className="form-label">New Password</label><input className="form-input" type="password" value={pwForm.new_password} onChange={e=>setPwForm(f=>({...f,new_password:e.target.value}))} placeholder="Min 8 chars, 1 uppercase, 1 digit" /></div>
          <button type="submit" className="btn btn-secondary" disabled={savingPw}>{savingPw?"Changing...":"Change Password"}</button>
        </form>
      </div>
    </div>
  );
}
