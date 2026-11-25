FROM nginx:alpine

# Configuration Nginx : sert la page et relaie /api/ vers le backend
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Fichiers statiques de l'application
COPY index.html style.css script.js /usr/share/nginx/html/

EXPOSE 80
