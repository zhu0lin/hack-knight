## Frontend Dockerfile for static Next.js export (Cloudflare-compatible)

FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Copy package files and install deps with lockfile
COPY package.json package-lock.json* ./
RUN npm ci

# Build the static site (Next.js output: 'export' -> out/)
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build-time configurable public API URL for static export
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Build; with output:'export' this produces /app/out
# If for any reason `out` is not created by build, fall back to `next export`.
RUN npm run build && [ -d out ] || npx next export

# Production image: serve the exported `out/` statically on port 3000
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

# Non-root user for safety
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Install a tiny static file server
RUN npm i -g serve

# Copy the static export
COPY --from=builder /app/out ./out

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["serve", "-s", "out", "-l", "3000"]

