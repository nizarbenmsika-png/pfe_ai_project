# ════════════════════════════════════════════════════════════════
# Dockerfile — Frontend EduAI (nginx)
# À placer dans : frontend/Dockerfile
# ════════════════════════════════════════════════════════════════

FROM nginx:alpine

# Remplacer la config nginx par la nôtre
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d/

# Copier index.html dans le dossier servi par nginx
COPY index.html /usr/share/nginx/html/

EXPOSE 80
