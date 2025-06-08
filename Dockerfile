# ============================
# BUILDER STAGE
# ============================
FROM node:22.16.0-bullseye-slim AS builder

# Install pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

# Copy root package files first for better caching
COPY package.json pnpm-lock.yaml ./

# Install all dependencies
RUN pnpm install

# Copy everything else
COPY . .

COPY src/ui/.env.production /app/src/ui/.env.production

# Add this before RUN npm run build
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL:-/api}

# Build from root - no need to cd since build script handles it
RUN pnpm run build

# ============================
# PRODUCTION STAGE
# ============================
FROM nginx:alpine

# Copy built files from builder
COPY --from=builder /app/src/ui/dist /usr/share/nginx/html

# Copy nginx config
COPY src/ui/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]