FROM node:latest as build
WORKDIR /app
COPY ./package* .
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:stable as server
COPY --from=build /app/dist/frontend/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
