"use client";

import { useEffect, useState } from "react";
import { conversations } from "@/lib/api";
import {
  MessageSquare,
  Send,
  Loader2,
  Search,
  Phone,
  User,
} from "lucide-react";

interface Conversation {
  id: string;
  contact_name: string;
  contact_phone?: string;
  last_message?: string;
  last_message_at?: string;
  unread_count?: number;
  channel?: string;
}

interface Message {
  id: string;
  content: string;
  direction: "inbound" | "outbound";
  created_at: string;
  sender_name?: string;
}

export default function ConversationsPage() {
  const [convList, setConvList] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [msgLoading, setMsgLoading] = useState(false);
  const [replyText, setReplyText] = useState("");
  const [sending, setSending] = useState(false);
  const [search, setSearch] = useState("");
  const [msgError, setMsgError] = useState("");

  useEffect(() => {
    conversations
      .list()
      .then((res: any) => {
        const items = res.items || res.conversations || res || [];
        setConvList(items);
      })
      .catch((err: any) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function selectConversation(id: string) {
    setSelectedId(id);
    setMsgLoading(true);
    try {
      const res: any = await conversations.get(id);
      setMessages(res.messages || res || []);
    } catch (err: any) {
      setMessages([]);
      setMsgError("حدث خطأ في تحميل الرسائل. حاول مرة أخرى.");
    } finally {
      setMsgLoading(false);
    }
  }

  async function handleReply(e: React.FormEvent) {
    e.preventDefault();
    if (!replyText.trim() || !selectedId) return;
    setSending(true);
    try {
      await conversations.reply(selectedId, replyText);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          content: replyText,
          direction: "outbound",
          created_at: new Date().toISOString(),
        },
      ]);
      setReplyText("");
    } catch (err: any) {
      setMsgError("فشل إرسال الرسالة. حاول مرة أخرى.");
    } finally {
      setSending(false);
    }
  }

  const filtered = convList.filter(
    (c) =>
      c.contact_name?.includes(search) || c.contact_phone?.includes(search)
  );

  const selectedConv = convList.find((c) => c.id === selectedId);

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
    <div className="bg-white rounded-xl border border-gray-200 flex h-[calc(100vh-10rem)] overflow-hidden">
      {/* Conversation list (left in RTL = right side visually) */}
      <div className="w-64 md:w-80 border-r border-gray-200 flex flex-col shrink-0">
        <div className="p-3 border-b border-gray-200">
          <div className="relative">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="بحث في المحادثات..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pr-9 pl-3 py-2 bg-gray-50 border border-gray-200 rounded-lg text-sm outline-none focus:ring-1 focus:ring-secondary"
            />
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {filtered.length === 0 ? (
            <div className="text-center py-10 text-gray-400 text-sm">
              <MessageSquare className="w-6 h-6 mx-auto mb-2 opacity-50" />
              لا توجد محادثات
            </div>
          ) : (
            filtered.map((conv) => (
              <button
                key={conv.id}
                onClick={() => selectConversation(conv.id)}
                className={`w-full text-start p-3 border-b border-gray-100 hover:bg-gray-50 transition ${
                  selectedId === conv.id ? "bg-secondary-50" : ""
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-green-100 text-green-700 rounded-full flex items-center justify-center text-sm font-bold shrink-0">
                    {conv.contact_name?.charAt(0) || "?"}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="font-medium text-gray-900 text-sm truncate">
                        {conv.contact_name}
                      </p>
                      {conv.unread_count ? (
                        <span className="bg-secondary text-white text-xs w-5 h-5 rounded-full flex items-center justify-center shrink-0">
                          {conv.unread_count}
                        </span>
                      ) : null}
                    </div>
                    <p className="text-xs text-gray-500 truncate mt-0.5">
                      {conv.last_message || "لا توجد رسائل"}
                    </p>
                  </div>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col">
        {selectedId ? (
          <>
            {/* Chat header */}
            <div className="p-4 border-b border-gray-200 flex items-center gap-3">
              <div className="w-9 h-9 bg-green-100 text-green-700 rounded-full flex items-center justify-center text-sm font-bold">
                {selectedConv?.contact_name?.charAt(0) || "?"}
              </div>
              <div>
                <p className="font-semibold text-gray-900 text-sm">
                  {selectedConv?.contact_name}
                </p>
                {selectedConv?.contact_phone && (
                  <p className="text-xs text-gray-500" dir="ltr">
                    {selectedConv.contact_phone}
                  </p>
                )}
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
              {msgError && (
                <div className="bg-red-50 text-red-600 text-sm p-3 rounded-lg text-center mb-2">
                  {msgError}
                  <button onClick={() => setMsgError("")} className="mr-2 underline">إغلاق</button>
                </div>
              )}
              {msgLoading ? (
                <div className="flex items-center justify-center py-10">
                  <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
                </div>
              ) : messages.length === 0 && !msgError ? (
                <div className="text-center py-10 text-gray-400 text-sm">
                  لا توجد رسائل بعد
                </div>
              ) : (
                messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex ${
                      msg.direction === "outbound"
                        ? "justify-end"
                        : "justify-start"
                    }`}
                  >
                    <div
                      className={`max-w-[70%] rounded-2xl px-4 py-2.5 text-sm ${
                        msg.direction === "outbound"
                          ? "bg-secondary text-white rounded-bl-sm"
                          : "bg-white border border-gray-200 text-gray-800 rounded-br-sm"
                      }`}
                    >
                      <p>{msg.content}</p>
                      <p
                        className={`text-xs mt-1 ${
                          msg.direction === "outbound"
                            ? "text-secondary-200"
                            : "text-gray-400"
                        }`}
                      >
                        {new Date(msg.created_at).toLocaleTimeString("ar-SA", {
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>

            {/* Reply input */}
            <form
              onSubmit={handleReply}
              className="p-3 border-t border-gray-200 flex items-center gap-2"
            >
              <input
                type="text"
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                placeholder="اكتب رسالة..."
                className="flex-1 px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm outline-none focus:ring-1 focus:ring-secondary"
              />
              <button
                type="submit"
                disabled={sending || !replyText.trim()}
                className="p-2.5 bg-secondary text-white rounded-lg hover:bg-secondary-600 transition disabled:opacity-50"
              >
                {sending ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </form>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-400">
            <div className="text-center">
              <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p className="text-sm">اختر محادثة للبدء</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
