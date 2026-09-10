# syntax=docker/dockerfile:1
# Frontend image — MULTI-STAGE BUILD.
#
# Stage 1 (build): node:20-alpine runs `npm ci && npm run build`.
# Stage 2 (serve): nginx:alpine serves dist/ on port 80.
#
# WHY nginx instead of `vite preview`:
#   - vite preview is a development-grade server; nginx is the standard static
#     production server (tiny image, gzip, cache headers).
#   - We need SPA history-API fallback (try_files ... /index.html) so routes
#     like /agents/:id/edit survive a hard refresh — configured below.

# ---------- stage 1: build ----------
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies from the lockfile only (deterministic, cached layer).
COPY package.json package-lock.json ./
RUN npm ci

# Copy just what the Vite build needs (avoids pulling host node_modules or
# other stray files into the build context).
COPY index.html vite.config.js ./
COPY src ./src

# Vite bakes VITE_* variables in at BUILD time. The browser calls the FastAPI
# backend. Use http://localhost:8000 for host-running (default), or override via
# compose build args for Docker internal access (e.g. http://backend:8000).
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

# ---------- stage 2: serve ----------
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

# SPA fallback config, written inline to keep this lane to one file.
RUN printf 'server {\n\
    listen       80;\n\
    server_name  _;\n\
    root         /usr/share/nginx/html;\n\
    index        index.html;\n\
\n\
    # SPA history-API fallback: unknown paths render the React router.\n\
    location / {\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
\n\
    # Hashed assets are immutable — cache hard.\n\
    location /assets/ {\n\
        expires 30d;\n\
        add_header Cache-Control "public, immutable";\n\
    }\n\
\n\
    gzip on;\n\
    gzip_types text/css application/javascript application/json image/svg+xml;\n\
}\n' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
