"use client";

import { useEffect, useState } from "react";
import { socialListening } from "@/lib/api";
import { Ear, Loader2, Check, X, MessageCircle, TrendingUp } from "lucide-react";

type Tab = "posts" | "pending" | "streams";

const priorityColors: Record<string, string> = {
  high: "bg-red-100 text-red-700",
  medium: "bg-yellow-100 text-yellow-700",
  low: "bg-gray-100 text-gray-600",
};

const statusColors: Record<string, string> = {
  pending: "bg-yellow-100 text-yellow-700",
  approved: "bg-green-100 text-green-700",
  rejected: "bg-red-100 text-red-700",
  published: "bg-blue-100 text-blue-700",
};

export default function SocialListeningPage() {
  const [tab, setTab] = useState<Tab>("posts");
  const [stats, setStats] = useState<any>(null);
  const [posts, setPosts] = useState<any[]>([]);
  const [pendingComments, setPendingComments] = useState<any[]>([]);
  const [streams, setStreams] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      socialListening.stats().catch(() => ({})),
      socialListening.posts().catch(() => ({ items: [] })),
      socialListening.pendingComments().catch(() => ({ items: [] })),
      socialListening.streams().catch(() => ({ items: [] })),
    ])
      .then(([s, p, c, st]) => {
        setStats(s);
        setPosts(p.items || []);
        setPendingComments(c.items || []);
        setStreams(st.items || []);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleReview = async (commentId: string, action: "approved" | "rejected") => {
    try {
      await socialListening.reviewComment(commentId, { status: action });
      setPendingComments((prev) => prev.filter((c) => c.id !== commentId));
    } catch (err) {
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-8 h-8 animate-spin text-secondary" />
      </div>
    );
  }

  return (
    <div>
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {[
          { label: "منشورات مكتشفة", value: stats?.posts_detected || 0, icon: TrendingUp },
          { label: "تعليقات بانتظار الموافقة", value: stats?.pending_comments || pendingComments.length, icon: MessageCircle },
          { label: "تعليقات منشورة", value: stats?.published_comments || 0, icon: Check },
          { label: "بث نشط", value: stats?.active_streams || streams.length, icon: Ear },
        ].map((s) => (
          <div key={s.label} className="bg-white rounded-xl border border-gray-200 p-4">
            <div className="flex items-center gap-2 text-gray-500 text-sm mb-1">
              <s.icon className="w-4 h-4" />
              {s.label}
            </div>
            <p className="text-2xl font-bold text-gray-900">{s.value}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-4">
        {[
          { key: "posts" as Tab, label: "المنشورات" },
          { key: "pending" as Tab, label: `بانتظار الموافقة (${pendingComments.length})` },
          { key: "streams" as Tab, label: "البث" },
        ].map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition ${
              tab === t.key ? "bg-secondary text-white" : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Posts tab */}
      {tab === "posts" && (
        <div className="space-y-3">
          {posts.length === 0 ? (
            <div className="bg-white rounded-xl border border-gray-200 p-10 text-center text-gray-400">
              <Ear className="w-8 h-8 mx-auto mb-2 opacity-50" />
              لا توجد منشورات مكتشفة
            </div>
          ) : (
            posts.map((post: any) => (
              <div key={post.id} className="bg-white rounded-xl border border-gray-200 p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-gray-900">{post.author_name || "مجهول"}</span>
                      <span className="text-xs text-gray-400">{post.platform}</span>
                      {post.priority && (
                        <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${priorityColors[post.priority] || priorityColors.low}`}>
                          {post.priority === "high" ? "عالي" : post.priority === "medium" ? "متوسط" : "منخفض"}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-700 line-clamp-3">{post.content}</p>
                  </div>
                  <div className="text-xs text-gray-400 shrink-0">
                    {post.relevance_score && `${Math.round(post.relevance_score * 100)}%`}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Pending comments tab */}
      {tab === "pending" && (
        <div className="space-y-3">
          {pendingComments.length === 0 ? (
            <div className="bg-white rounded-xl border border-gray-200 p-10 text-center text-gray-400">
              <Check className="w-8 h-8 mx-auto mb-2 opacity-50" />
              لا توجد تعليقات بانتظار الموافقة
            </div>
          ) : (
            pendingComments.map((comment: any) => (
              <div key={comment.id} className="bg-white rounded-xl border border-gray-200 p-4">
                <div className="flex items-center gap-2 mb-2 text-xs text-gray-400">
                  <span className={`px-2 py-0.5 rounded-full font-medium ${statusColors[comment.status] || statusColors.pending}`}>
                    {comment.status === "pending" ? "بانتظار" : comment.status}
                  </span>
                  <span>{comment.draft_type}</span>
                  <span>{comment.account_type}</span>
                </div>
                <p className="text-sm text-gray-800 mb-3">{comment.content}</p>
                <div className="flex gap-2 justify-end">
                  <button
                    onClick={() => handleReview(comment.id, "rejected")}
                    className="px-3 py-1.5 text-sm text-red-600 hover:bg-red-50 rounded-lg transition flex items-center gap-1"
                  >
                    <X className="w-4 h-4" />
                    رفض
                  </button>
                  <button
                    onClick={() => handleReview(comment.id, "approved")}
                    className="px-3 py-1.5 text-sm bg-green-600 text-white hover:bg-green-700 rounded-lg transition flex items-center gap-1"
                  >
                    <Check className="w-4 h-4" />
                    موافقة
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Streams tab */}
      {tab === "streams" && (
        <div className="space-y-3">
          {streams.length === 0 ? (
            <div className="bg-white rounded-xl border border-gray-200 p-10 text-center text-gray-400">
              <Ear className="w-8 h-8 mx-auto mb-2 opacity-50" />
              لا يوجد بث نشط
            </div>
          ) : (
            streams.map((stream: any) => (
              <div key={stream.id} className="bg-white rounded-xl border border-gray-200 p-4 flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">{stream.name}</p>
                  <p className="text-xs text-gray-500">{stream.platform} - {stream.stream_type}</p>
                </div>
                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${stream.is_active ? "bg-green-100 text-green-700" : "bg-gray-100 text-gray-600"}`}>
                  {stream.is_active ? "نشط" : "متوقف"}
                </span>
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
