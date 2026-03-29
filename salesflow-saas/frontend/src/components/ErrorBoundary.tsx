"use client";

import { Component, type ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("ErrorBoundary caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      return (
        <div className="flex min-h-[400px] items-center justify-center" dir="rtl">
          <div className="text-center">
            <AlertTriangle className="mx-auto h-12 w-12 text-warning" />
            <h2 className="mt-4 text-xl font-bold text-gray-900">
              حدث خطأ غير متوقع
            </h2>
            <p className="mt-2 text-gray-500">
              نعتذر عن هذا الخطأ. يرجى تحديث الصفحة والمحاولة مرة أخرى.
            </p>
            <button
              onClick={() => {
                this.setState({ hasError: false, error: undefined });
                window.location.reload();
              }}
              className="mt-6 inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-white hover:bg-primary-700"
            >
              <RefreshCw className="h-4 w-4" />
              تحديث الصفحة
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
