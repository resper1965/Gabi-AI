# Frontend Dockerfile - Gabi AI Agent
# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Set environment variables for build
ENV NEXT_TELEMETRY_DISABLED=1
ENV NODE_ENV=production

# Build the application
RUN pnpm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install production dependencies
RUN pnpm install --prod --frozen-lockfile

# Copy built application
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# Create entrypoint script
RUN echo '#!/bin/sh\n\
set -e\n\
\n\
echo "🚀 Starting Gabi AI Frontend..."\n\
\n\
# Replace environment variables in runtime\n\
if [ -n "$NEXT_PUBLIC_API_URL" ]; then\n\
  echo "✅ API URL configured: $NEXT_PUBLIC_API_URL"\n\
fi\n\
\n\
# Start the application\n\
echo "🌐 Starting Next.js server..."\n\
exec node server.js\n\
' > /app/start.sh && chmod +x /app/start.sh

# Set environment
ENV NODE_ENV=production
ENV PORT=3000
ENV NEXT_TELEMETRY_DISABLED=1

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start application
CMD ["/app/start.sh"] 