/**
 * Dealix API Client — Type-safe fetch wrapper with JWT auth.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// ─── Token Management ───

let accessToken: string | null = null;

export function setToken(token: string | null) {
  accessToken = token;
  if (token) {
    if (typeof window !== "undefined") localStorage.setItem("dealix_token", token);
  } else {
    if (typeof window !== "undefined") localStorage.removeItem("dealix_token");
  }
}

export function getToken(): string | null {
  if (accessToken) return accessToken;
  if (typeof window !== "undefined") {
    accessToken = localStorage.getItem("dealix_token");
  }
  return accessToken;
}

// ─── Base Fetch ───

async function apiFetch<T = any>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (res.status === 401) {
    setToken(null);
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw new Error("غير مصرح — يرجى تسجيل الدخول");
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `خطأ ${res.status}`);
  }

  return res.json();
}

// ─── Auth API ───

export const auth = {
  async login(email: string, password: string) {
    const data = await apiFetch<{ access_token: string; user: any }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setToken(data.access_token);
    return data;
  },

  async register(payload: { email: string; password: string; full_name: string; company_name: string; phone?: string }) {
    const data = await apiFetch<{ access_token: string; user: any }>("/auth/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setToken(data.access_token);
    return data;
  },

  logout() {
    setToken(null);
    if (typeof window !== "undefined") window.location.href = "/login";
  },

  async me() {
    return apiFetch<{ user: any }>("/auth/me");
  },
};

// ─── Leads API ───

export const leads = {
  list: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return apiFetch(`/leads${qs}`);
  },
  get: (id: string) => apiFetch(`/leads/${id}`),
  create: (data: any) => apiFetch("/leads", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: any) => apiFetch(`/leads/${id}`, { method: "PUT", body: JSON.stringify(data) }),
};

// ─── Deals API ───

export const deals = {
  list: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return apiFetch(`/deals${qs}`);
  },
  get: (id: string) => apiFetch(`/deals/${id}`),
  create: (data: any) => apiFetch("/deals", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: any) => apiFetch(`/deals/${id}`, { method: "PUT", body: JSON.stringify(data) }),
};

// ─── Dashboard API ───

export const dashboard = {
  overview: () => apiFetch("/dashboard/overview"),
  pipeline: () => apiFetch("/dashboard/pipeline"),
};

// ─── Conversations API ───

export const conversations = {
  list: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return apiFetch(`/conversations${qs}`);
  },
  get: (id: string) => apiFetch(`/conversations/${id}`),
  reply: (id: string, message: string) =>
    apiFetch(`/conversations/${id}/reply`, { method: "POST", body: JSON.stringify({ message }) }),
};

// ─── Appointments API ───

export const appointments = {
  list: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return apiFetch(`/appointments${qs}`);
  },
  today: () => apiFetch("/appointments/today"),
  availability: (date: string, serviceType?: string) => {
    const params = new URLSearchParams({ date });
    if (serviceType) params.set("service_type", serviceType);
    return apiFetch(`/appointments/availability?${params}`);
  },
  stats: () => apiFetch("/appointments/stats"),
  create: (data: any) => apiFetch("/appointments", { method: "POST", body: JSON.stringify(data) }),
  confirm: (id: string) => apiFetch(`/appointments/${id}/confirm`, { method: "POST" }),
  complete: (id: string) => apiFetch(`/appointments/${id}/complete`, { method: "POST" }),
  cancel: (id: string) => apiFetch(`/appointments/${id}`, { method: "DELETE" }),
};

// ─── Analytics API ───

export const analytics = {
  overview: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return apiFetch(`/analytics/overview${qs}`);
  },
  pipeline: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return apiFetch(`/analytics/pipeline${qs}`);
  },
  revenue: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return apiFetch(`/analytics/revenue${qs}`);
  },
};

// ─── AI Agents API ───

export const aiAgents = {
  list: () => apiFetch("/ai/agents"),
  create: (data: any) => apiFetch("/ai/agents", { method: "POST", body: JSON.stringify(data) }),
  stats: () => apiFetch("/ai/stats"),
  discover: (data: any) => apiFetch("/ai/discover", { method: "POST", body: JSON.stringify(data) }),
  chat: (data: any) => apiFetch("/ai/chat", { method: "POST", body: JSON.stringify(data) }),
};

// ─── Notifications API ───

export const notifications = {
  list: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return apiFetch(`/notifications${qs}`);
  },
  markRead: (id: string) => apiFetch(`/notifications/${id}/read`, { method: "POST" }),
  markAllRead: () => apiFetch("/notifications/read-all", { method: "POST" }),
};

// ─── Voice API ───

export const voice = {
  profiles: () => apiFetch("/voice/profiles"),
  call: (data: any) => apiFetch("/voice/call", { method: "POST", body: JSON.stringify(data) }),
  calls: () => apiFetch("/voice/calls"),
};
