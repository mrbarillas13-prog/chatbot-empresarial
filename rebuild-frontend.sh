#!/bin/bash
set -e

echo "Building frontend for production..."
docker exec chatbot-frontend npm run build

echo "Copying dist to nginx..."
rm -rf /var/www/chatbotexpert
cp -r /root/chatbot-empresarial/frontend/dist /var/www/chatbotexpert

echo "Reloading nginx..."
nginx -t && systemctl reload nginx

echo "Done! Production build deployed."

