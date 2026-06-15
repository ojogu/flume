import { createMDX } from 'fumadocs-mdx/next';

const withMDX = createMDX();

/** @type {import('next').NextConfig} */
const config = {
  assetPrefix: '/docs',
  output: 'standalone',
  reactStrictMode: true,
};

export default withMDX(config);
