### Build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install --legacy-peer-deps
COPY . .
RUN npm run build

### Production stage (static serving)
FROM nginx:1.25-alpine
COPY --from=build /app/dist /usr/share/nginx/html
# Basic nginx config tweak: disable default logs verbosity optional
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
