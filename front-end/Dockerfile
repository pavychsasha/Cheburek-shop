FROM node:20-bullseye

WORKDIR /app

COPY package.json .
RUN npm i

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
