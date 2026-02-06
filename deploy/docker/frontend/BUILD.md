# Frontend Docker Build Guide

## Image Information
- **Image Name**: `todo-frontend`
- **Base Image**: `node:20-alpine`
- **Build Context**: `frontend/`
- **Exposed Port**: `3000`
- **Production Port**: `3000`

## Quick Start

### Build the Image
```bash
# From project root (Phase-04/)
docker build \
  -f deploy/docker/frontend/Dockerfile \
  -t todo-frontend:1.0.0-local \
  -t todo-frontend:latest \
  ./frontend
```

### Build with No Cache (Clean Build)
```bash
docker build \
  --no-cache \
  -f deploy/docker/frontend/Dockerfile \
  -t todo-frontend:1.0.0-local \
  -t todo-frontend:latest \
  ./frontend
```

### Run the Container
```bash
# Basic run
docker run -p 3000:3000 todo-frontend:latest

# With environment variables
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:5000 \
  todo-frontend:latest

# With env file
docker run -p 3000:3000 \
  --env-file frontend/.env.production \
  todo-frontend:latest
```

### Verify Running Container
```bash
# Check container status
docker ps

# View logs
docker logs <container-id>

# Follow logs
docker logs -f <container-id>

# Access the application
curl http://localhost:3000
```

## Multi-Stage Build Breakdown

### Stage 1: Dependencies (deps)
- **Purpose**: Install all dependencies for build process
- **Base**: `node:20-alpine`
- **Actions**:
  - Installs `libc6-compat` for npm package compatibility
  - Copies `package.json` and `package-lock.json`
  - Runs `npm ci` for reproducible dependency installation
- **Output**: `/app/node_modules` with all dependencies

### Stage 2: Builder
- **Purpose**: Build the Next.js application
- **Base**: `node:20-alpine`
- **Actions**:
  - Copies `node_modules` from deps stage
  - Copies all source code
  - Sets `NODE_ENV=production`
  - Runs `npm run build` to create production bundles
  - Generates standalone output (minimal dependencies)
- **Output**:
  - `.next/standalone/` - Optimized server files
  - `.next/static/` - Static assets
  - `public/` - Public assets

### Stage 3: Runner (Production)
- **Purpose**: Minimal production runtime image
- **Base**: `node:20-alpine`
- **Actions**:
  - Creates non-root user `nextjs` (UID 1001)
  - Copies only necessary runtime files from builder
  - Sets production environment variables
  - Exposes port 3000
  - Implements health check
  - Runs as non-root user for security
- **Final Image Size**: ~200-300 MB (optimized)

## Security Features

### Non-Root User
```dockerfile
# Creates system group and user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Switches to non-root user
USER nextjs
```

### File Ownership
All application files are owned by `nextjs:nodejs` to prevent unauthorized modifications.

### Health Check
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"
```

### Environment Variables
- Never hardcode secrets in Dockerfile
- Use `.env` files or Kubernetes secrets
- `.dockerignore` prevents `.env` files from being copied

## Optimization Features

### Layer Caching
Dependencies are copied separately from source code to leverage Docker layer caching:
```dockerfile
# Copy package files first
COPY package.json package-lock.json ./
RUN npm ci

# Copy source code later (changes more frequently)
COPY . .
```

### Standalone Output
Next.js standalone mode (`output: 'standalone'` in `next.config.ts`):
- Includes only necessary runtime dependencies
- Reduces final image size by ~50%
- Faster container startup times

### .dockerignore
Excludes unnecessary files from build context:
- `node_modules` (installed fresh in container)
- `.next` build cache
- `.env` files (security)
- Development files, logs, documentation

## Environment Variables

### Build-Time Variables
- `NODE_ENV=production` - Optimizes build for production
- `NEXT_TELEMETRY_DISABLED=1` - Disables Next.js telemetry

### Runtime Variables
- `PORT=3000` - Application port
- `HOSTNAME=0.0.0.0` - Listen on all interfaces
- `NEXT_PUBLIC_API_URL` - Backend API URL (must be set at runtime)

### Required Environment Variables for Production
Create a `.env.production` file or set in Kubernetes:
```env
NEXT_PUBLIC_API_URL=https://api.example.com
NEXT_PUBLIC_WS_URL=wss://api.example.com
```

## Troubleshooting

### Build Fails: "Cannot find module"
- Ensure all dependencies are in `package.json`
- Try clean build with `--no-cache`
- Check that `node_modules` is in `.dockerignore`

### Container Exits Immediately
- Check logs: `docker logs <container-id>`
- Verify `server.js` exists in standalone output
- Ensure all required environment variables are set

### Health Check Fails
- Container may need more than 40s to start (increase `start-period`)
- Verify port 3000 is not blocked
- Check application logs for startup errors

### Large Image Size
- Verify standalone mode is enabled in `next.config.ts`
- Ensure `.dockerignore` is present and comprehensive
- Check that only necessary files are copied in runner stage

### Permission Errors
- Verify files are owned by `nextjs:nodejs` user
- Check that `USER nextjs` directive is present
- Ensure no root-only operations in startup scripts

## Validation Checklist

Before deploying to production:
- [ ] Image builds successfully without errors
- [ ] Health check passes after startup
- [ ] Application accessible on port 3000
- [ ] Environment variables properly externalized
- [ ] No secrets or `.env` files in image
- [ ] Running as non-root user (`nextjs`)
- [ ] Image size is optimized (<500 MB)
- [ ] Logs show clean startup without warnings
- [ ] Container stops gracefully on SIGTERM

## Image Inspection

### View Image Details
```bash
# List images
docker images | grep todo-frontend

# Inspect image
docker inspect todo-frontend:latest

# View image layers
docker history todo-frontend:latest

# Check image size
docker images todo-frontend:latest --format "{{.Repository}}:{{.Tag}} - {{.Size}}"
```

### Verify Security
```bash
# Check user inside container
docker run --rm todo-frontend:latest id

# List files and ownership
docker run --rm todo-frontend:latest ls -la /app

# Check for secrets (should find none)
docker run --rm todo-frontend:latest env | grep -i secret
```

## Next Steps
1. Test the image locally
2. Push to container registry (if needed)
3. Deploy to Kubernetes cluster
4. Configure ingress for external access
5. Set up monitoring and logging

## Related Files
- `frontend/package.json` - Dependencies and build scripts
- `frontend/next.config.ts` - Next.js configuration (standalone mode)
- `deploy/docker/frontend/.dockerignore` - Build context exclusions
- `deploy/kubernetes/frontend/` - Kubernetes deployment manifests (to be created)
