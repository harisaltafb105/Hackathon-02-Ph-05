# ==============================================================================
# Multi-stage Dockerfile for Next.js Frontend (Production-Optimized)
# ==============================================================================
# Build Context: frontend/
# Image Name: todo-frontend
# Base Image: node:20-alpine
# Exposed Port: 3000
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Dependencies
# Purpose: Install all dependencies (production + dev) for build process
# ------------------------------------------------------------------------------
FROM node:20-alpine AS deps

# Add libc6-compat for compatibility with certain npm packages
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package files for dependency installation
# Leverage Docker cache - only reinstall if package files change
COPY package.json package-lock.json ./

# Install dependencies using npm ci for reproducible builds
RUN npm ci

# ------------------------------------------------------------------------------
# Stage 2: Builder
# Purpose: Build the Next.js application for production
# ------------------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy all source files needed for build
COPY . .

# Set environment variable for production build
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Build the Next.js application
# This generates optimized production bundles in .next directory
RUN npm run build

# ------------------------------------------------------------------------------
# Stage 3: Runner (Production Image)
# Purpose: Minimal production image with only runtime dependencies
# ------------------------------------------------------------------------------
FROM node:20-alpine AS runner

WORKDIR /app

# Set production environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user for security
# nextjs group (GID 1001) and nextjs user (UID 1001)
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy necessary files from builder stage
# Using Next.js standalone output for minimal production footprint
# Standalone mode includes only necessary dependencies
COPY --from=builder --chown=nextjs:nodejs /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Set ownership to non-root user
RUN chown -R nextjs:nodejs /app

# Switch to non-root user
USER nextjs

# Expose port 3000 for Next.js application
EXPOSE 3000

# Set port environment variable
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Health check to verify application is running
# Next.js doesn't have a default health endpoint, so we check the root
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start the Next.js production server
CMD ["node", "server.js"]
