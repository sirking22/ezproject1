# syntax=docker/dockerfile:1

FROM node:20-alpine AS builder
WORKDIR /app

# Install deps using lockfile if present
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm \
    if [ -f package-lock.json ]; then npm ci; else npm install; fi

# Copy source
COPY . .

# Build-time configuration for Vite
ARG VITE_DEMO=1
ARG VITE_API_URL=
ENV VITE_DEMO=${VITE_DEMO}
ENV VITE_API_URL=${VITE_API_URL}

# Build static site
RUN npm run build


FROM nginx:1.27-alpine AS runtime

# Nginx config: SPA fallback + gzip
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY docker-entrypoint.d/ /docker-entrypoint.d/

# Static assets
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=10s CMD wget -qO- http://localhost/ >/dev/null 2>&1 || exit 1

# Default nginx CMD/ENTRYPOINT stay from base image


