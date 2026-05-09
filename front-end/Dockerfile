FROM node:22-bookworm-slim

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

ENV VITE_DEV_SERVER_HOST=0.0.0.0 \
    VITE_DEV_SERVER_PORT=5178

EXPOSE 5178

CMD ["npm", "run", "dev"]
