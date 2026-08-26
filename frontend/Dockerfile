# ============================================================
# SevaSetu AI — Frontend Dockerfile (Multi-stage)
# Author: Rahul Jha | Made in India 🇮🇳
# Stage 1: Build React app
# Stage 2: Serve with Nginx
# ============================================================

# ── Stage 1: Build ────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

# Build args (set in docker-compose or CI)
ARG REACT_APP_API_URL=http://localhost:8000
ARG REACT_APP_APP_NAME="SevaSetu AI"
ARG REACT_APP_VERSION=1.0.0

ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_APP_NAME=$REACT_APP_APP_NAME
ENV REACT_APP_VERSION=$REACT_APP_VERSION

# Install dependencies (cached layer)
COPY package*.json ./
RUN npm ci --silent

# Copy source and build
COPY . .
RUN npm run build

# ── Stage 2: Serve ────────────────────────────────────────────
FROM nginx:alpine AS production

# Remove default nginx config
RUN rm -f /etc/nginx/conf.d/default.conf

# Copy custom nginx config for SPA routing
COPY docker/nginx-frontend.conf /etc/nginx/conf.d/default.conf

# Copy React build
COPY --from=builder /app/build /usr/share/nginx/html

# Security: non-root
RUN adduser -D -g '' nginxuser && \
    chown -R nginxuser:nginxuser /usr/share/nginx/html && \
    chown -R nginxuser:nginxuser /var/cache/nginx && \
    touch /var/run/nginx.pid && \
    chown nginxuser:nginxuser /var/run/nginx.pid

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD wget -qO- http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
