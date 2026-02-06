import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  output: 'standalone', // Optimizes for Docker deployment with minimal dependencies
};

export default nextConfig;
