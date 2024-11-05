import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,  // Ativa o modo estrito para debugging de erros comuns
  // Remova 'swcMinify' se não suportada ou necessária 
};

export default nextConfig;
