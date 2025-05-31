# ============================
# BUILDER STAGE
# ============================
FROM node:20-alpine AS builder

# Set working directory
WORKDIR /app

# Install pnpm globally
RUN npm install -g pnpm

# Copy package files
COPY package.json pnpm-lock.yaml* ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source files
COPY . .

# Create symlink for axios in services directory to fix import resolution
RUN mkdir -p /app/../services/node_modules && \
    ln -sf /app/node_modules/axios /app/../services/node_modules/

# Build the application
RUN pnpm run build

# ============================
# PRODUCTION STAGE
# ============================
FROM nginx:alpine

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
