# /etc/nginx/conf.d/site_template.conf

index index.html;

location ~* \.(?:xml|txt)$ {
    try_files $uri =404;
    add_header Content-Type $content_type;
    add_header Cache-Control "public, max-age=3600";
}

location /_astro/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

location ~* \.(?:jpg|jpeg|gif|png|ico|svg|webp|woff2?)$ {
    expires 7d;
    add_header Cache-Control "public, no-transform";
}

location / {
    try_files $uri $uri/ /index.html;
    add_header Cache-Control "no-cache";
    proxy_set_header X-Forwarded-Port 80;
    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    port_in_redirect off;
    absolute_redirect off;
}