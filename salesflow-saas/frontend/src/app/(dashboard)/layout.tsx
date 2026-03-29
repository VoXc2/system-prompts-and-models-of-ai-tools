"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import { getToken, auth } from "@/lib/api";
import { notifications as notificationsApi } from "@/lib/api";
import {
  LayoutDashboard,
  Users,
  UserCheck,
  Handshake,
  MessageSquare,
  Calendar,
  Bot,
  Brain,
  BarChart3,
  Ear,
  Settings,
  Bell,
  LogOut,
  Menu,
  X,
  ChevronDown,
  Zap,
  Code2,
} from "lucide-react";
import ErrorBoundary from "@/components/ErrorBoundary";

const navItems = [
  { href: "/dashboard", label: "لوحة التحكم", icon: LayoutDashboard },
  { href: "/dashboard/leads", label: "العملاء المحتملين", icon: Users },
  { href: "/dashboard/customers", label: "العملاء", icon: UserCheck },
  { href: "/dashboard/deals", label: "الصفقات", icon: Handshake },
  { href: "/dashboard/conversations", label: "المحادثات", icon: MessageSquare },
  { href: "/dashboard/appointments", label: "المواعيد", icon: Calendar },
  { href: "/dashboard/social-listening", label: "الاستماع الاجتماعي", icon: Ear },
  { href: "/dashboard/ai-agents", label: "الوكلاء الأذكياء", icon: Bot },
  { href: "/dashboard/ai-traces", label: "حوكمة AI", icon: Brain },
  { href: "/dashboard/analytics", label: "التحليلات", icon: BarChart3 },
  { href: "/dashboard/automations", label: "الأتمتة", icon: Zap },
  { href: "/dashboard/widget", label: "الودجت", icon: Code2 },
  { href: "/dashboard/settings", label: "الإعدادات", icon: Settings },
];

function getPageTitle(pathname: string): string {
  const item = navItems.find((n) => n.href === pathname);
  return item?.label || "لوحة التحكم";
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [user, setUser] = useState<any>(null);
  const [authChecked, setAuthChecked] = useState(false);

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push("/login");
      return;
    }
    auth
      .me()
      .then((data) => {
        setUser(data.user);
        setAuthChecked(true);
      })
      .catch(() => {
        router.push("/login");
      });
  }, [router]);

  if (!authChecked) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-10 h-10 border-4 border-secondary border-t-transparent rounded-full animate-spin mx-auto mb-3" />
          <p className="text-gray-500 text-sm">جاري التحميل...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed top-0 right-0 h-full w-64 bg-primary-900 text-white z-50 transform transition-transform duration-200 lg:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "translate-x-full lg:translate-x-0"
        } lg:static lg:z-auto`}
      >
        <div className="p-5 border-b border-primary-700 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/logo-dark.svg" alt="Dealix" className="h-8 w-8" />
            <h1 className="text-xl font-bold tracking-wide">Dealix</h1>
          </div>
          <button
            onClick={() => setSidebarOpen(false)}
            className="lg:hidden text-primary-300 hover:text-white"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <nav className="mt-4 px-3 space-y-1">
          {navItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setSidebarOpen(false)}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition ${
                  active
                    ? "bg-secondary text-white"
                    : "text-primary-200 hover:bg-primary-800 hover:text-white"
                }`}
              >
                <item.icon className="w-5 h-5 shrink-0" />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="absolute bottom-0 right-0 left-0 p-3 border-t border-primary-700">
          <button
            onClick={() => auth.logout()}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-primary-300 hover:bg-primary-800 hover:text-white w-full transition"
          >
            <LogOut className="w-5 h-5" />
            تسجيل الخروج
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-h-screen lg:mr-0">
        {/* Top header */}
        <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
          <div className="flex items-center justify-between px-4 lg:px-6 py-3">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden text-gray-600 hover:text-gray-900"
              >
                <Menu className="w-6 h-6" />
              </button>
              <h2 className="text-lg font-bold text-primary-900">
                {getPageTitle(pathname)}
              </h2>
            </div>

            <div className="flex items-center gap-3">
              {/* Notification bell */}
              <button className="relative p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-lg transition">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1 left-1 w-2 h-2 bg-red-500 rounded-full" />
              </button>

              {/* User menu */}
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-2 p-2 hover:bg-gray-100 rounded-lg transition"
                >
                  <div className="w-8 h-8 bg-secondary-100 text-secondary-700 rounded-full flex items-center justify-center text-sm font-bold">
                    {user?.full_name?.charAt(0) || "U"}
                  </div>
                  <span className="hidden sm:block text-sm font-medium text-gray-700">
                    {user?.full_name || "المستخدم"}
                  </span>
                  <ChevronDown className="w-4 h-4 text-gray-400" />
                </button>

                {userMenuOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-40"
                      onClick={() => setUserMenuOpen(false)}
                    />
                    <div className="absolute left-0 top-full mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-50 py-1">
                      <div className="px-4 py-2 border-b border-gray-100">
                        <p className="text-sm font-medium text-gray-900">
                          {user?.full_name}
                        </p>
                        <p className="text-xs text-gray-500">{user?.email}</p>
                      </div>
                      <Link
                        href="/dashboard/settings"
                        onClick={() => setUserMenuOpen(false)}
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        الإعدادات
                      </Link>
                      <button
                        onClick={() => auth.logout()}
                        className="block w-full text-start px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                      >
                        تسجيل الخروج
                      </button>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 lg:p-6">
          <ErrorBoundary>{children}</ErrorBoundary>
        </main>
      </div>
    </div>
  );
}
