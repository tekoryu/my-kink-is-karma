# Production Dockerfile for Vue 3 app (multi-stage)
FROM node:20-alpine AS build

WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install all dependencies (including dev) needed for build
RUN npm install && npm cache clean --force

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Final stage: Nginx to serve built assets
FROM nginx:alpine

# Copy custom nginx config (provides SPA routing and optional API proxy)
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built application
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

