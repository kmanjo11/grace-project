# ============================
# BUILDER STAGE
# ============================
FROM node:20 AS builder

# Set working directory
WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install --no-frozen-lockfile

# Copy source files
COPY . .

# Create symlink for axios
RUN mkdir -p /app/../services/node_modules && \
    ln -sf /app/node_modules/axios /app/../services/node_modules/

# Set working directory to UI
WORKDIR /app/src/ui

# Install UI dependencies and build with specific Rollup version
RUN pnpm install && \
    pnpm add -D rollup@3.29.4 && \
    pnpm install --no-optional && \
    pnpm run build

# ============================
# PRODUCTION STAGE
# ============================
FROM nginx:alpine

# Copy built files from builder stage
COPY --from=builder /app/src/ui/dist /usr/share/nginx/html

# Copy nginx configuration
COPY deployment/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]