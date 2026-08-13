FROM nginx:1.29-alpine
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s CMD wget -q -O /dev/null http://localhost:8080/gateway-health || exit 1
