# syntax=docker/dockerfile:1
FROM node:22-alpine AS base
WORKDIR /app

# Install dependencies
FROM base AS dependencies
COPY package.json package-lock.json* ./
RUN npm ci --only=production

# Runner stage
FROM base AS runner
ENV NODE_ENV=production
RUN addgroup -g 1001 -S nodejs && adduser -S nodejs -u 1001
COPY --from=dependencies /app/node_modules ./node_modules
COPY package.json ./
COPY src ./src

# Create storage directory with appropriate permissions
RUN mkdir -p /app/data/storage && chown -R nodejs:nodejs /app

USER nodejs
EXPOSE 5000
CMD ["node", "src/server.js"]

