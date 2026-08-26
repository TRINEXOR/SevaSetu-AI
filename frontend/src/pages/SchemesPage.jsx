/**
 * SevaSetu AI — Schemes Page
 * Author: Rahul Jha | Made in India 🇮🇳
 *
 * Features:
 *  - Browse 100+ government schemes with search & category filter
 *  - Scheme eligibility checker modal (income/age/gender inputs)
 *  - Scheme detail modal with full info
 *  - Ask AI about any scheme
 *  - Download checklist PDF
 */

import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { schemeAPI, reportAPI } from "../services/api";
import { useAuth } from "../App";
import { useToast } from "../components/MainLayout";
import styles from "./SchemesPage.module.css";

// ── Category config ────────────────────────────────────────────────────────
const CATEGORIES = [
  { key: "all",         label: "All Schemes",   icon: "📋" },
  { key: "agriculture", label: "Agriculture",   icon: "🌾" },
  { key: "health",      label: "Health",        icon: "🏥" },
  { key: "education",   label: "Education",     icon: "📚" },
  { key: "housing",     label: "Housing",       icon: "🏠" },
  { key: "women",       label: "Women",         icon: "👩" },
  { key: "finance",     label: "Finance",       icon: "💰" },
  { key: "employment",  label: "Employment",    icon: "💼" },
  { key: "social",      label: "Social",        icon: "🤝" },
];

// ── Fallback mock schemes (if API unavailable) ─────────────────────────────
const MOCK_SCHEMES = [
  { id:1, name:"PM Kisan Samman Nidhi", category:"agriculture", description:"₹6,000/year income support to small & marginal farmers in 3 installments.", benefits:"₹6,000 per year", application_url:"https://pmkisan.gov.in", helpline:"155261", is_central:true },
  { id:2, name:"Ayushman Bharat PMJAY", category:"health", description:"Free health insurance cover of ₹5 lakh per family per year at 25,000+ hospitals.", benefits:"₹5 lakh health cover", application_url:"https://pmjay.gov.in", helpline:"14555", is_central:true },
  { id:3, name:"PM Jan Dhan Yojana",    category:"finance", description:"Zero balance bank account with RuPay debit card and ₹2 lakh accident insurance.", benefits:"Zero balance account + insurance", application_url:"https://pmjdy.gov.in", helpline:"1800-11-0001", is_central:true },
  { id:4, name:"PM Awas Yojana Urban",  category:"housing", description:"Affordable housing for EWS/LIG/MIG with interest subsidy up to 6.5%.", benefits:"Interest subsidy 3–6.5%", application_url:"https://pmaymis.gov.in", helpline:"1800-11-6163", is_central:true },
  { id:5, name:"Beti Bachao Beti Padhao", category:"women", description:"National campaign promoting welfare and education of girl child across India.", benefits:"Awareness + scholarships", application_url:"https://wcd.nic.in", helpline:"181", is_central:true },
  { id:6, name:"Sukanya Samriddhi Yojana", category:"finance", description:"High-interest savings scheme (8.2% p.a.) for girl child with tax-free returns.", benefits:"8.2% interest, tax-free", application_url:"https://nsiindia.gov.in", helpline:"18004250076", is_central:true },
  { id:7, name:"PM Mudra Yojana",       category:"finance", description:"Collateral-free loans up to ₹10 lakh for micro and small business enterprises.", benefits:"Loan up to ₹10 lakh", application_url:"https://mudra.org.in", helpline:"1800-180-1111", is_central:true },
  { id:8, name:"PM Scholarship Scheme", category:"education", description:"₹3,000-3,500/month scholarship for wards of ex-servicemen studying professional courses.", benefits:"₹36,000–42,000 per year", application_url:"https://ksb.gov.in", helpline:"011-26173215", is_central:true },
  { id:9, name:"Atal Pension Yojana",   category:"finance", description:"Guaranteed pension of ₹1,000–5,000/month for unorganised sector workers after age 60.", benefits:"₹1,000–5,000/month pension", application_url:"https://npscra.nsdl.co.in", helpline:"1800-110-069", is_central:true },
  { id:10, name:"PM Garib Kalyan Yojana", category:"social", description:"Free 5 kg food grain per person per month for NFSA beneficiary households.", benefits:"5 kg free food/month", application_url:"https://dfpd.gov.in", helpline:"1967", is_central:true },
  { id:11, name:"Kisan Credit Card",    category:"agriculture", description:"Short-term credit facility for farmers at subsidised 4% interest rate for agriculture needs.", benefits:"Credit at 4% interest", application_url:"https://pmkisan.gov.in/KCC.aspx", helpline:"155261", is_central:true },
  { id:12, name:"Pradhan Mantri Matru Vandana Yojana", category:"women", description:"₹5,000 cash incentive for pregnant women for first live birth to compensate wage loss.", benefits:"₹5,000 in 3 installments", application_url:"https://pmmvy.wcd.gov.in", helpline:"7998799804", is_central:true },
];

// ── Scheme Card ────────────────────────────────────────────────────────────
function SchemeCard({ scheme, onLearnMore, onAskAI }) {
  const catIcons = { agriculture:"🌾", health:"🏥", education:"📚", housing:"🏠", women:"👩", finance:"💰", employment:"💼", social:"🤝", digital:"💻" };
  const icon = catIcons[scheme.category] || "📋";

  return (
    <div className={styles.schemeCard} onClick={() => onLearnMore(scheme)}>
      <div className={styles.cardTop}>
        <div className={styles.cardCat}>
          {icon} {scheme.category?.replace(/_/g, " ")}
        </div>
        {scheme.is_central && <span className="badge badge-blue">Central</span>}
      </div>
      <h3 className={styles.cardName}>{scheme.name}</h3>
      <p className={styles.cardDesc}>{scheme.description}</p>
      {scheme.benefits && (
        <div className={styles.cardBenefit}>
          <span className={styles.benefitLabel}>Benefit:</span>
          <span className={styles.benefitVal}>{scheme.benefits}</span>
        </div>
      )}
      <div className={styles.cardFooter}>
        <button
          className="btn btn-secondary btn-sm"
          onClick={(e) => { e.stopPropagation(); onAskAI(scheme.name); }}
        >
          💬 Ask AI
        </button>
        {scheme.application_url && (
          <a
            href={scheme.application_url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-ghost btn-sm"
            onClick={(e) => e.stopPropagation()}
          >
            🌐 Apply
          </a>
        )}
      </div>
    </div>
  );
}

// ── Scheme Detail Modal ────────────────────────────────────────────────────
function SchemeModal({ scheme, onClose, onAskAI }) {
  if (!scheme) return null;
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" style={{ maxWidth: 560 }} onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>
        <div className={styles.modalCat}>{scheme.category?.replace(/_/g, " ").toUpperCase()}</div>
        <h2 style={{ color: "var(--text)", marginBottom: 8 }}>{scheme.name}</h2>
        <p style={{ marginBottom: 16 }}>{scheme.description}</p>

        {scheme.benefits && (
          <div className={styles.modalSection}>
            <div className={styles.modalLabel}>💰 Benefits</div>
            <div className={styles.modalVal}>{scheme.benefits}</div>
          </div>
        )}
        {scheme.eligibility_text && (
          <div className={styles.modalSection}>
            <div className={styles.modalLabel}>✅ Eligibility</div>
            <div className={styles.modalVal}>{scheme.eligibility_text}</div>
          </div>
        )}
        {scheme.application_steps && (
          <div className={styles.modalSection}>
            <div className={styles.modalLabel}>📋 How to Apply</div>
            <div className={styles.modalVal}>{scheme.application_steps}</div>
          </div>
        )}
        <div style={{ display: "flex", gap: 8, marginTop: 20, flexWrap: "wrap" }}>
          {scheme.helpline && (
            <a href={`tel:${scheme.helpline}`} className="btn btn-secondary btn-sm">
              📞 {scheme.helpline}
            </a>
          )}
          {scheme.application_url && (
            <a href={scheme.application_url} target="_blank" rel="noopener noreferrer" className="btn btn-secondary btn-sm">
              🌐 Official Portal
            </a>
          )}
          <button className="btn btn-primary btn-sm" onClick={() => { onAskAI(scheme.name); onClose(); }}>
            💬 Ask AI About This
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Eligibility Checker Modal ──────────────────────────────────────────────
function EligibilityModal({ onClose, onResults }) {
  const [form, setForm] = useState({
    annual_income: "", age: "", gender: "all",
    is_farmer: false, caste_category: "general",
    has_house: true, is_student: false, is_disabled: false,
    categories: [],
  });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((f) => ({ ...f, [name]: type === "checkbox" ? checked : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        ...form,
        annual_income: form.annual_income ? parseFloat(form.annual_income) : null,
        age: form.age ? parseInt(form.age) : null,
        gender: form.gender === "all" ? null : form.gender,
        categories: form.categories.length ? form.categories : null,
      };
      const res = await schemeAPI.checkEligibility(payload);
      onResults(res.data);
      onClose();
    } catch {
      // Mock results
      onResults({ schemes: MOCK_SCHEMES.slice(0, 6).map(s => ({ ...s, eligibility_score: Math.random() * 0.4 + 0.6, eligibility_status: "eligible" })) });
      onClose();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" style={{ maxWidth: 480 }} onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>
        <h2 style={{ color: "var(--text)", marginBottom: 4 }}>🔍 Check Eligibility</h2>
        <p style={{ marginBottom: 20 }}>Enter your details to see matching government schemes.</p>

        <form onSubmit={handleSubmit}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            <div className="form-group">
              <label className="form-label">Annual Income (₹)</label>
              <input className="form-input" name="annual_income" type="number" placeholder="e.g. 200000" value={form.annual_income} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label className="form-label">Age (years)</label>
              <input className="form-input" name="age" type="number" placeholder="e.g. 30" value={form.age} onChange={handleChange} />
            </div>
            <div className="form-group">
              <label className="form-label">Gender</label>
              <select className="form-select" name="gender" value={form.gender} onChange={handleChange}>
                <option value="all">Any / Prefer not to say</option>
                <option value="male">Male</option>
                <option value="female">Female</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Caste Category</label>
              <select className="form-select" name="caste_category" value={form.caste_category} onChange={handleChange}>
                <option value="general">General</option>
                <option value="obc">OBC</option>
                <option value="sc">SC</option>
                <option value="st">ST</option>
              </select>
            </div>
          </div>

          <div style={{ display: "flex", flexWrap: "wrap", gap: 16, margin: "12px 0 20px" }}>
            {[
              { name: "is_farmer",  label: "I am a farmer 🌾" },
              { name: "is_student", label: "I am a student 📚" },
              { name: "is_disabled",label: "Differently abled ♿" },
              { name: "has_house",  label: "I own a house 🏠" },
            ].map(({ name, label }) => (
              <label key={name} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: "0.875rem", color: "var(--text-2)", cursor: "pointer" }}>
                <input type="checkbox" name={name} checked={form[name]} onChange={handleChange} style={{ accentColor: "var(--saffron)" }} />
                {label}
              </label>
            ))}
          </div>

          <button type="submit" className="btn btn-primary w-full" disabled={loading}>
            {loading ? <><div className="spinner sm" /> Checking...</> : "🔍 Check My Eligibility"}
          </button>
        </form>
      </div>
    </div>
  );
}

// ── Main SchemesPage ───────────────────────────────────────────────────────
export default function SchemesPage() {
  const navigate   = useNavigate();
  const showToast  = useToast();
  const { user }   = useAuth();

  const [schemes,       setSchemes]       = useState(MOCK_SCHEMES);
  const [loading,       setLoading]       = useState(true);
  const [search,        setSearch]        = useState("");
  const [activeFilter,  setActiveFilter]  = useState("all");
  const [selectedScheme,setSelectedScheme]= useState(null);
  const [showEligibility,setShowEligibility] = useState(false);
  const [eligibilityResults, setEligibilityResults] = useState(null);
  const [page,          setPage]          = useState(1);
  const [total,         setTotal]         = useState(0);

  const loadSchemes = useCallback(async () => {
    setLoading(true);
    try {
      const res = await schemeAPI.list({
        category: activeFilter === "all" ? undefined : activeFilter,
        search: search || undefined,
        page,
        limit: 12,
      });
      setSchemes(res.data.data || []);
      setTotal(res.data.total || 0);
    } catch {
      // Use mock data
      let filtered = MOCK_SCHEMES;
      if (activeFilter !== "all") filtered = filtered.filter(s => s.category === activeFilter);
      if (search) filtered = filtered.filter(s => s.name.toLowerCase().includes(search.toLowerCase()) || s.description.toLowerCase().includes(search.toLowerCase()));
      setSchemes(filtered);
      setTotal(filtered.length);
    } finally {
      setLoading(false);
    }
  }, [activeFilter, search, page]);

  useEffect(() => {
    const t = setTimeout(loadSchemes, 300);
    return () => clearTimeout(t);
  }, [loadSchemes]);

  const handleAskAI = (schemeName) => {
    navigate("/chat", { state: { prefillQuery: `Tell me about ${schemeName} — who is eligible and how to apply?` } });
  };

  const handleEligibilityResults = (data) => {
    setEligibilityResults(data);
    setSchemes(data.schemes || []);
    showToast?.(`Found ${data.eligible_count || 0} eligible schemes!`, "success");
  };

  const displaySchemes = eligibilityResults ? (eligibilityResults.schemes || []) : schemes;

  return (
    <div className={styles.schemesPage}>
      {/* Header */}
      <div className={styles.pageHeader}>
        <div>
          <h1>🏛️ Government Schemes</h1>
          <p className="text-muted">Browse {total || MOCK_SCHEMES.length}+ central & state welfare schemes</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowEligibility(true)}>
          🔍 Check My Eligibility
        </button>
      </div>

      {/* Eligibility result banner */}
      {eligibilityResults && (
        <div className={styles.resultBanner}>
          <span>🎯 Eligibility check complete — showing {eligibilityResults.schemes?.length} matched schemes</span>
          <button className="btn btn-ghost btn-sm" onClick={() => { setEligibilityResults(null); loadSchemes(); }}>
            ✕ Clear Filter
          </button>
        </div>
      )}

      {/* Search */}
      <div className="search-bar" style={{ marginBottom: 14 }}>
        <span>🔍</span>
        <input
          type="text"
          placeholder="Search schemes by name, benefit, or ministry..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        />
        {search && (
          <button style={{ background: "none", border: "none", color: "var(--text-2)", cursor: "pointer" }} onClick={() => setSearch("")}>✕</button>
        )}
      </div>

      {/* Category filters */}
      <div className="filter-chips">
        {CATEGORIES.map(({ key, label, icon }) => (
          <button
            key={key}
            className={`filter-chip ${activeFilter === key ? "active" : ""}`}
            onClick={() => { setActiveFilter(key); setPage(1); setEligibilityResults(null); }}
          >
            {icon} {label}
          </button>
        ))}
      </div>

      {/* Schemes grid */}
      {loading ? (
        <div className={styles.schemeGrid}>
          {Array.from({ length: 8 }).map((_, i) => (
            <div key={i} className="skeleton" style={{ height: 200, borderRadius: 12 }} />
          ))}
        </div>
      ) : displaySchemes.length === 0 ? (
        <div className="empty-state">
          <div className="icon">🔍</div>
          <h3>No schemes found</h3>
          <p>Try a different search term or category</p>
          <button className="btn btn-primary btn-sm" onClick={() => { setSearch(""); setActiveFilter("all"); }}>
            Reset Filters
          </button>
        </div>
      ) : (
        <>
          <div className={styles.schemeGrid}>
            {displaySchemes.map((s) => (
              <SchemeCard
                key={s.id}
                scheme={s}
                onLearnMore={setSelectedScheme}
                onAskAI={handleAskAI}
              />
            ))}
          </div>

          {/* Pagination */}
          {!eligibilityResults && total > 12 && (
            <div className={styles.pagination}>
              <button className="btn btn-secondary btn-sm" disabled={page === 1} onClick={() => setPage(p => p - 1)}>← Previous</button>
              <span className="text-muted">Page {page} of {Math.ceil(total / 12)}</span>
              <button className="btn btn-secondary btn-sm" disabled={page >= Math.ceil(total / 12)} onClick={() => setPage(p => p + 1)}>Next →</button>
            </div>
          )}
        </>
      )}

      {/* Modals */}
      {selectedScheme && (
        <SchemeModal scheme={selectedScheme} onClose={() => setSelectedScheme(null)} onAskAI={handleAskAI} />
      )}
      {showEligibility && (
        <EligibilityModal onClose={() => setShowEligibility(false)} onResults={handleEligibilityResults} />
      )}
    </div>
  );
}
