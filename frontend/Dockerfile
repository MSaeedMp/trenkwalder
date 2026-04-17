FROM node:20-alpine

RUN corepack enable && corepack prepare pnpm@latest --activate

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . .

ENV VITE_API_URL=http://trenkwalder-backend:8000

EXPOSE 5173

CMD ["pnpm", "dev", "--host"]
