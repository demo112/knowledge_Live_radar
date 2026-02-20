import type { NextConfig } from "next";
import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin();

const nextConfig: NextConfig = {
  // 1. 日志配置：提升开发调试体验，在控制台显示详细的 fetch URL
  logging: {
    fetches: {
      fullUrl: true,
    },
  },

  // 2. 开发指示器：禁用以避免遮挡错误日志
  devIndicators: false,

  // 3. 严格模式：建议开启，有助于在开发阶段发现潜在问题
  reactStrictMode: true,

  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'http://127.0.0.1:8000/api/v1/:path*',
      },
    ];
  },
};

export default withNextIntl(nextConfig);
