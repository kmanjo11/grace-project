# ============================================
# Builder Stage - For production build
# ============================================
FROM node:18.20.2 AS builder

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@8.10.0

# Copy package files for better layer caching
COPY package*.json pnpm-lock.yaml* ./
COPY src/ui/package*.json ./src/ui/

# ============================================
# Builder Stage - For production build
# ============================================
FROM node:18.20.2 AS builder

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@8.10.0

# Copy package files
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build the application
RUN pnpm run build

# ============================================
# Production Stage - Optimized for production
# ============================================
FROM nginx:1.25.3-alpine AS production

# Install curl for healthcheck
RUN apk --no-cache add curl

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Set proper permissions
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chmod -R 755 /usr/share/nginx/html

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

# Expose port 80
EXPOSE 80

# Environment variables
ENV NODE_ENV=production

# Start nginx
CMD ["nginx", "-g", "daemon off;"]

# ============================================
# Development Stage - For local development
# ============================================
FROM node:18.20.2 AS development

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm@8.10.0

# Copy package files
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install

# Copy source code
COPY . .

# Expose port for development server
EXPOSE 3000

# Start development server
CMD ["pnpm", "dev"]

# ============================================
# Test Stage - For running tests
# ============================================
FROM development AS test

# Run tests
CMD ["pnpm", "test:ci"]
