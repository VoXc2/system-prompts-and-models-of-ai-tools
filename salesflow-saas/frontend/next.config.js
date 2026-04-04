/** @type {import('next').NextConfig} */
/**
 * Marketing static files: frontend/public/dealix-* (sync: node scripts/sync-marketing-to-public.cjs)
 * Redirects fix 404 when opening /dealix-marketing without index.html (Next static serving).
 */
const nextConfig = {
  output: "standalone",
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
      {
        source: "/investors",
        destination: "/dealix-marketing/investor/00-investor-dealix-full-ar.html",
        permanent: false,
      },
      {
        source: "/investors/",
        destination: "/dealix-marketing/investor/00-investor-dealix-full-ar.html",
        permanent: false,
      },
    ];
  },
};

module.exports = nextConfig;
