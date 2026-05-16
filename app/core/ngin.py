import os
import inspect

from app.models.sites_models import Site, NginxSiteConfig


def get_site_nginx_config(nginx_config: NginxSiteConfig):
    if not nginx_config:
        return None

    includes = [
        "include /etc/nginx/conf.d/common_settings.inc;",
        "include /etc/nginx/conf.d/site_template.inc;",
        "include /etc/nginx/conf.d/site_api_template.inc;"
    ]

    includes_str = "\n    ".join(includes)

    client_set = f'set $client_id "{nginx_config.site.slug}";' if nginx_config.site.slug else ''
    extra = nginx_config.extra_config or ''


    template = inspect.cleandoc(f"""
        server {{
            listen {nginx_config.port};
            root {nginx_config.full_root_path};
            {client_set}

            {includes_str}

            {extra}
        }}
    """)
    return template


def generate_nginx_file(site: Site, config_dir):
    content = get_site_nginx_config(site.nginx_config)
    if not content:
        print(f"No Nginx config for site {site.slug}")
        return None

    file_name = f"{site.slug}.conf"
    full_path = os.path.join(config_dir, file_name)

    try:
        with open(full_path, "w") as f:
            f.write(content)

        print(f"Successfully generated/updated: {full_path}")
        return full_path
    except Exception as e:
        print(f"Error writing Nginx config for {site.slug}: {e}")
        return None