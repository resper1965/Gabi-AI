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

# Build the application
RUN pnpm run build

# Production stage
FROM node:20-alpine AS runner

WORKDIR /app

# Install pnpm
RUN npm install -g pnpm

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install production dependencies
RUN pnpm install --prod --frozen-lockfile

# Copy built application
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/next.config.mjs ./

# Create entrypoint script
RUN echo '#!/bin/sh\n\
# Replace environment variables in runtime\n\
if [ -n "$NEXT_PUBLIC_API_URL" ]; then\n\
  echo "Setting NEXT_PUBLIC_API_URL to: $NEXT_PUBLIC_API_URL"\n\
fi\n\
\n\
# Start the application\n\
exec node server.js\n\
' > /app/start.sh && chmod +x /app/start.sh

# Set environment
ENV NODE_ENV=production
ENV PORT=3000

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start application
CMD ["/app/start.sh"] 