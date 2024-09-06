FROM node:20-alpine3.19

WORKDIR /app
RUN apk add --no-cache python3 make g++

COPY package.json .

RUN npm install

COPY . .

EXPOSE 3000

CMD [ "npm", "start" ]