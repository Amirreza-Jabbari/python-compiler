# nginx/Dockerfile
FROM nginx:alpine
# Copy our custom Nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf
# We don't need to copy frontend files here as they're served from the frontend container
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
