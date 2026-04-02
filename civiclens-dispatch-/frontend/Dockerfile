# frontend/Dockerfile
# Multi-stage Docker build for the CivicLens Dispatch React frontend
#
# Stage 1 (build): Install dependencies and build static files
# Stage 2 (serve): Serve the built files with a lightweight Node server
#
# Multi-stage builds keep the final image small — the build tools
# (node_modules, build cache) are discarded after the build is done.
#
# Day 58: Docker containerization

# ========================================
# STAGE 1: BUILD
# ========================================
# Use Node.js 20 to install dependencies and build the React app
# "AS build" names this stage so we can reference it later
FROM node:20-alpine AS build

# Set working directory inside the container
WORKDIR /app

# Copy package files FIRST for layer caching
# If package.json hasn't changed, Docker reuses the cached node_modules
COPY package.json package-lock.json ./

# Install all dependencies
# npm ci is like npm install but faster and stricter:
#   - Uses exact versions from package-lock.json
#   - Deletes existing node_modules first
#   - Fails if package.json and lock file don't match
RUN npm ci

# Copy the rest of the frontend source code
COPY . .

# Set the API URL for the production build
# When built inside Docker, the frontend needs to know where the backend is
# In docker-compose, the backend is accessible at http://backend:8000
# But the BROWSER makes the requests, not the container, so we use localhost
ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=$VITE_API_URL

# Build the React app for production
# This creates optimized static files in the /app/dist directory
# Vite compiles JSX, bundles JavaScript, minifies CSS, etc.
RUN npm run build


# ========================================
# STAGE 2: SERVE
# ========================================
# Use a lightweight Node image to serve the built files
# We don't need the full build tools anymore — just a static file server
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install 'serve' — a simple static file server
# This serves the built HTML/CSS/JS files to browsers
# -g installs it globally so we can use the 'serve' command
RUN npm install -g serve

# Copy ONLY the built files from Stage 1
# This is the key benefit of multi-stage builds:
# The final image doesn't include node_modules, source code, or build tools
# Just the compiled static files (~1-5 MB vs ~500 MB with everything)
COPY --from=build /app/dist ./dist

# Document that this container listens on port 3000
EXPOSE 3000

# Start the static file server
# serve -s dist — serves the dist directory with single-page app (SPA) support
# -s flag means: for any route that doesn't match a file, serve index.html
#   This is needed for client-side routing in React
# -l 3000 — listen on port 3000
CMD ["serve", "-s", "dist", "-l", "3000"]