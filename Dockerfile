FROM node:22-alpine AS base
RUN npm install -g pnpm

FROM base AS deps
WORKDIR /app

COPY package*.json ./
COPY pnpm*.yaml ./

RUN pnpm install --frozen-lockfile


FROM base AS build

WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

RUN pnpm dlx prisma generate
RUN pnpm run build
RUN pnpm prune --prod

FROM base AS runtime
WORKDIR /app
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/dist ./dist
COPY --from=build /app/prisma ./prisma
COPY --from=build /app/package.json ./package.json

CMD ["node", "dist/src/index.js"]