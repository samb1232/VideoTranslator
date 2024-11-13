# frontend/Dockerfile
FROM node:alpine AS frontend_build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build


FROM nginx:stable-alpine
COPY --from=frontend_build /app/dist /usr/share/nginx/html
COPY --from=frontend_build /app/nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx", "-g", "daemon  off;"]
