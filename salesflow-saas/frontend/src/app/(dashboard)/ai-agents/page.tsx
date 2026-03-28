"use client";

import { useEffect, useState } from "react";
import { aiAgents } from "@/lib/api";
import {
  Bot,
  MessageSquare,
  Users,
  Handshake,
  Zap,
  Loader2,
  Search,
  Activity,
} from "lucide-react";

interface AgentStats {
  active_agents: number;
  messages_sent: number;
  leads_discovered: number;
  deals_created: number;
}

interface Agent {
  id: string;
  name: string;
  type?: string;
  status: string;
  messages_sent?: number;
  leads_generated?: number;
  created_at?: string;
}

const statCards = [
  {
    key: "active_agents" as const,
    label: "وكلاء نشطون",
    icon: Bot,
    color: "bg-green-100 text-green-600",
  },
  {
    key: "messages_sent" as const,
    label: "رسائل مرسلة",
    icon: MessageSquare,
    color: "bg-blue-100 text-blue-600",
  },
  {
    key: "leads_discovered" as const,
    label: "عملاء مكتشفون",
    icon: Users,
    color: "bg-purple-100 text-purple-600",
  },
  {
    key: "deals_created" as const,
    label: "صفقات",
    icon: Handshake,
    color: "bg-orange-100 text-orange-600",
  },
];

export default function AIAgentsPage() {
  const [stats, setStats] = useState<AgentStats | null>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [discovering, setDiscovering] = useState(false);

  useEffect(() => {
    Promise.all([
      aiAgents.stats().catch(() => null),
      aiAgents.list().catch(() => []),
    ])
      .then(([statsRes, listRes]: any[]) => {
        setStats(statsRes);
        setAgents(listRes.items || listRes.agents || listRes || []);
      })
      .catch((err: any) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function handleDiscover() {
    setDiscovering(true);
    try {
      await aiAgents.discover({ type: "leads" });
    } catch {
      // silent
    } finally {
      setDiscovering(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-secondary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
        {error}
      </div>
    );
  }

  return (
    <div>
      {/* Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {statCards.map((card) => (
          <div
            key={card.key}
            className="bg-white rounded-xl border border-gray-200 p-5"
          >
            <div className="flex items-center gap-3">
              <div
                className={`w-10 h-10 rounded-lg flex items-center justify-center ${card.color}`}
              >
                <card.icon className="w-5 h-5" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {stats?.[card.key]?.toLocaleString("ar-SA") ?? "0"}
                </p>
                <p className="text-xs text-gray-500">{card.label}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Discovery button */}
      <div className="mb-6 flex justify-end">
        <button
          onClick={handleDiscover}
          disabled={discovering}
          className="bg-secondary hover:bg-secondary-600 text-white px-5 py-2.5 rounded-lg text-sm font-medium flex items-center gap-2 transition disabled:opacity-60"
        >
          {discovering ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <Search className="w-4 h-4" />
          )}
          اكتشاف عملاء
        </button>
      </div>

      {/* Agent list */}
      <div className="bg-white rounded-xl border border-gray-200">
        <div className="p-4 border-b border-gray-200">
          <h3 className="font-bold text-gray-900">الوكلاء</h3>
        </div>

        {agents.length === 0 ? (
          <div className="p-10 text-center text-gray-400 text-sm">
            <Bot className="w-8 h-8 mx-auto mb-2 opacity-50" />
            لا يوجد وكلاء بعد
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {agents.map((agent) => (
              <div
                key={agent.id}
                className="p-4 flex items-center justify-between hover:bg-gray-50 transition"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-primary-50 text-primary-600 rounded-lg flex items-center justify-center">
                    <Bot className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 text-sm">
                      {agent.name}
                    </p>
                    {agent.type && (
                      <p className="text-xs text-gray-500">{agent.type}</p>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-4">
                  {agent.messages_sent != null && (
                    <span className="text-xs text-gray-500">
                      {agent.messages_sent} رسالة
                    </span>
                  )}
                  {agent.leads_generated != null && (
                    <span className="text-xs text-gray-500">
                      {agent.leads_generated} عميل
                    </span>
                  )}
                  <div className="flex items-center gap-1.5">
                    <span
                      className={`w-2 h-2 rounded-full ${
                        agent.status === "active"
                          ? "bg-green-500"
                          : agent.status === "paused"
                          ? "bg-yellow-500"
                          : "bg-gray-400"
                      }`}
                    />
                    <span className="text-xs text-gray-500">
                      {agent.status === "active"
                        ? "نشط"
                        : agent.status === "paused"
                        ? "متوقف"
                        : agent.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
