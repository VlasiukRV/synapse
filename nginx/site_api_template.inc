# /etc/nginx/conf.d/site_api_template.inc

location /api/ {

            proxy_pass http://host.docker.internal:8000;
            proxy_set_header X-Client-ID $client_id;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;

            proxy_read_timeout 90;
            proxy_connect_timeout 90;
        }