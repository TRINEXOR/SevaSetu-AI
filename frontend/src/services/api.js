/**
 * SevaSetu AI — API Service Layer
 * Author: Rahul Jha | Made in India 🇮🇳
 *
 * Gemini/RAG mode is used through the FastAPI backend.
 */

import axios from "axios";

const configuredBaseUrl = (process.env.REACT_APP_API_URL || window.location.origin).trim();
const BASE_URL = configuredBaseUrl.replace(/\/$/, "").replace(/\/api\/v1$/, "");

// ── Axios Instance ─────────────────────────────────────────────────────────
const api = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 60000,
  headers: { "Content-Type": "application/json" },
});

// ── Request Interceptor: Inject JWT ────────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("ss_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── Response Interceptor: Handle 401 ──────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      localStorage.clear();
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ── Error Helper ──────────────────────────────────────────────────────────
export const getErrorMessage = (error) => {
  if (error.response?.data?.detail)  return error.response.data.detail;
  if (error.response?.data?.message) return error.response.data.message;
  if (error.message === "Network Error") return "Network error. Please check the backend service and try again.";
  if (error.code === "ECONNABORTED")     return "Request timed out. Please try again.";
  return "Something went wrong. Please try again.";
};

// ═══════════════════════════════════════════════════════════════════════════
// AUTH
// ═══════════════════════════════════════════════════════════════════════════

export const authAPI = {
  register:       (data)            => api.post("/auth/register", data),
  login:          (email, password) => api.post("/auth/login",
    new URLSearchParams({ username: email, password }),
    { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
  ),
  refresh:        (token)           => api.post("/auth/refresh", { refresh_token: token }),
  logout:         ()                => api.post("/auth/logout"),
  me:             ()                => api.get("/auth/me"),
  changePassword: (data)            => api.post("/auth/change-password", data),
  forgotPassword: (email)           => api.post("/auth/forgot-password", { email }),
  resetPassword:  (token, password) => api.post("/auth/reset-password", { token, new_password: password }),
};

// ═══════════════════════════════════════════════════════════════════════════
// AI QUERIES — backend/Gemini powered
// ═══════════════════════════════════════════════════════════════════════════

export const queryAPI = {
  ask: (question, language = "en", category = null) =>
    api.post("/queries/ask", { question, language, category }),
  getHistory: (page = 1, limit = 10, category = null, search = null) =>
    api.get("/queries/history", { params: { page, limit, category, search } }),
  getSuggestions: (category = null, language = "en") =>
    api.get("/queries/suggestions", { params: { category, language } }),
  getQuery:       (id)  => api.get(`/queries/${id}`),
  deleteQuery:    (id)  => api.delete(`/queries/${id}`),
  submitFeedback: (qid, rating, comment, isHelpful) =>
    api.post("/queries/feedback", { query_id: qid, rating, comment, is_helpful: isHelpful }),
};

// ═══════════════════════════════════════════════════════════════════════════
// SCHEMES
// ═══════════════════════════════════════════════════════════════════════════

export const schemeAPI = {
  list:             (params = {})  => api.get("/schemes/",        { params }),
  getCategories:    ()             => api.get("/schemes/categories"),
  getScheme:        (id)           => api.get(`/schemes/${id}`),
  checkEligibility: (data)         => api.post("/schemes/eligibility", data),
  createScheme:     (data)         => api.post("/schemes/", data),
  updateScheme:     (id, data)     => api.put(`/schemes/${id}`, data),
  deleteScheme:     (id)           => api.delete(`/schemes/${id}`),
};

// ═══════════════════════════════════════════════════════════════════════════
// DOCUMENTS
// ═══════════════════════════════════════════════════════════════════════════

export const documentAPI = {
  upload: (file, serviceType) => {
    const form = new FormData();
    form.append("file", file);
    if (serviceType) form.append("service_type", serviceType);
    return api.post("/documents/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
      timeout: 120000,
    });
  },
  list:         (page = 1, serviceType = null) => api.get("/documents/", { params: { page, service_type: serviceType } }),
  getDocument:  (id)          => api.get(`/documents/${id}`),
  getChecklist: (serviceType) => api.get(`/documents/checklist/${serviceType}`),
  deleteDocument:(id)         => api.delete(`/documents/${id}`),
};

// ═══════════════════════════════════════════════════════════════════════════
// REPORTS / PDF
// ═══════════════════════════════════════════════════════════════════════════

const _downloadBlob = (blob, filename) => {
  const url  = window.URL.createObjectURL(new Blob([blob]));
  const link = document.createElement("a");
  link.href  = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const reportAPI = {
  downloadQueryPDF: async (queryId) => {
    const res = await api.get(`/reports/query/${queryId}`, { responseType: "blob" });
    _downloadBlob(res.data, `sevasetu_query_${queryId}.pdf`);
  },
  downloadHistoryPDF: async () => {
    const res = await api.get("/reports/history", { responseType: "blob" });
    _downloadBlob(res.data, "sevasetu_history.pdf");
  },
  downloadChecklistPDF: async (serviceType) => {
    const res = await api.get(`/reports/checklist/${serviceType}`, { responseType: "blob" });
    _downloadBlob(res.data, `sevasetu_checklist_${serviceType}.pdf`);
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// ADMIN
// ═══════════════════════════════════════════════════════════════════════════

export const adminAPI = {
  getDashboard:  ()            => api.get("/admin/dashboard"),
  getUsers:      (params = {}) => api.get("/admin/users", { params }),
  updateUser:    (id, data)    => api.put(`/admin/users/${id}`, data),
  getAllQueries: (params = {}) => api.get("/admin/queries", { params }),
  getDailyStats: (days = 7)   => api.get("/admin/stats/daily",   { params: { days } }),
  getSchemeStats:()            => api.get("/admin/stats/schemes"),
};

// ═══════════════════════════════════════════════════════════════════════════
// USERS
// ═══════════════════════════════════════════════════════════════════════════

export const userAPI = {
  updateProfile: (data)     => api.put("/users/me", data),
  updateLanguage:(language) => api.patch("/users/me/language", { language }),
};

export default api;
