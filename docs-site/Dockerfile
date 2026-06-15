FROM node:20-alpine AS builder
WORKDIR /app

COPY docs-site/package.json ./
RUN npm install --legacy-peer-deps

COPY docs-site/ ./
COPY openapi.json /openapi.json

RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=3001

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3001
CMD ["node", "server.js"]
