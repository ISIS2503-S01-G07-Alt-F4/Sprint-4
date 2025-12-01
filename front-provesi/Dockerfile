# Stage 1: Build the React application
FROM node:25-alpine3.21 AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build
RUN 

CMD ["npm", "run", "dev"]