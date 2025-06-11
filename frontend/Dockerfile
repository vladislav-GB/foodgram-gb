# build stage
FROM node:21.7.1-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . ./
RUN npm run build

# production stage
FROM nginx:1.25-alpine
COPY --from=build /app/build /usr/share/nginx/html

