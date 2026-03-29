/**
 * Dealix API Client — Type-safe fetch wrapper with JWT auth.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "/api/v1";

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

// ─── Tenant API ───

export const tenant = {
  get: () => apiFetch("/tenant"),
  update: (data: any) => apiFetch("/tenant", { method: "PUT", body: JSON.stringify(data) }),
};

// ─── Voice API ───

export const voice = {
  profiles: () => apiFetch("/voice/profiles"),
  call: (data: any) => apiFetch("/voice/call", { method: "POST", body: JSON.stringify(data) }),
  calls: () => apiFetch("/voice/calls"),
};

// ─── Customers API ───

export const customers = {
  list: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return apiFetch(`/customers${qs}`);
  },
  get: (id: string) => apiFetch(`/customers/${id}`),
  create: (data: any) => apiFetch("/customers", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: any) => apiFetch(`/customers/${id}`, { method: "PUT", body: JSON.stringify(data) }),
};

// ─── Activities API ───

export const activities = {
  list: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return apiFetch(`/activities${qs}`);
  },
  create: (data: any) => apiFetch("/activities", { method: "POST", body: JSON.stringify(data) }),
};

// ─── AI Traces (Governance) API ───

export const aiTraces = {
  list: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return apiFetch(`/ai/traces${qs}`);
  },
  stats: () => apiFetch("/ai/traces/stats"),
};

// ─── Social Listening API ───

export const socialListening = {
  streams: () => apiFetch("/social/streams"),
  createStream: (data: any) => apiFetch("/social/streams", { method: "POST", body: JSON.stringify(data) }),
  posts: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return apiFetch(`/social/posts${qs}`);
  },
  pendingComments: () => apiFetch("/social/comments/pending"),
  reviewComment: (id: string, data: any) => apiFetch(`/social/comments/${id}/review`, { method: "POST", body: JSON.stringify(data) }),
  stats: () => apiFetch("/social/stats"),
};

// ─── Growth Events / Attribution API ───

export const growthEvents = {
  track: (data: any) => apiFetch("/growth-events/track", { method: "POST", body: JSON.stringify(data) }),
  journey: (leadId: string) => apiFetch(`/growth-events/journey/${leadId}`),
  channels: () => apiFetch("/growth-events/channels"),
  campaigns: () => apiFetch("/growth-events/campaigns"),
};

// ─── Integrations API ───

export const integrations = {
  list: () => apiFetch("/integrations"),
  connect: (data: any) => apiFetch("/integrations", { method: "POST", body: JSON.stringify(data) }),
  disconnect: (id: string) => apiFetch(`/integrations/${id}`, { method: "DELETE" }),
  status: (id: string) => apiFetch(`/integrations/${id}/status`),
};

// ─── Audit Logs API ───

export const auditLogs = {
  list: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return apiFetch(`/audit-logs${qs}`);
  },
};

// ─── Subscription API ───

export const subscription = {
  get: () => apiFetch("/subscription"),
  update: (data: any) => apiFetch("/subscription", { method: "PUT", body: JSON.stringify(data) }),
};

// ─── Messages API ───

export const messages = {
  list: (params?: Record<string, string>) => {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    return apiFetch(`/messages${qs}`);
  },
  scheduled: () => apiFetch("/messages/scheduled"),
};
