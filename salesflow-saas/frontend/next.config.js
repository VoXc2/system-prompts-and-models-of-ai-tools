/** @type {import('next').NextConfig} */
/**
 * Marketing static files: frontend/public/dealix-* (sync: node scripts/sync-marketing-to-public.cjs)
 * Redirects fix 404 when opening /dealix-marketing without index.html (Next static serving).
 */
const nextConfig = {
  output: "standalone",
  /** إخفاء مؤشر Next Dev Tools (النقطة الزرقاء / nextjs-portal) أثناء التطوير */
  devIndicators: false,
  experimental: {
    optimizePackageImports: ["lucide-react"],
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          {
            key: "Permissions-Policy",
            value: "camera=(), microphone=(), geolocation=()",
          },
        ],
      },
    ];
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
        pathname: "/**",
      },
    ],
  },
  async redirects() {
    return [
      /* ملفات .md تحت dealix-marketing: إعادة التوجيه من middleware (src/middleware.ts) */
      {
        source: "/dealix-marketing",
        destination: "/dealix-marketing/index.html",
        permanent: false,
      },
      {
        source: "/dealix-marketing/",
        destination: "/dealix-marketing/index.html",
        permanent: false,
      },
      {
        source: "/dealix-presentations",
        destination: "/dealix-presentations/00-dealix-company-master-ar.html",
        permanent: false,
      },
      {
        source: "/dealix-presentations/",
        destination: "/dealix-presentations/00-dealix-company-master-ar.html",
        permanent: false,
      },
    ];
  },
};

module.exports = nextConfig;
