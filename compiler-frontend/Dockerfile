# frontend/Dockerfile
FROM node:23-alpine as builder
WORKDIR /app
# Copy dependency files and install
COPY package.json yarn.lock ./
RUN yarn install
# Copy the rest of the source code and build
COPY . .
RUN yarn build

# Use an official Nginx image to serve the production build
FROM nginx:alpine
# Copy the build output from the builder stage to the Nginx html folder.
COPY --from=builder /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
