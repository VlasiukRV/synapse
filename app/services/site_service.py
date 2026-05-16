import os

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
import docker

from app.core.ngin import generate_nginx_file
from app.models.sites_models import Site, BuildLog, NginxSiteConfig
from app.schemas.sites_schemas import SiteCreate, NginxConfigCreate
from app.core.site_build_manager import BuildManager

NGINX_CONFIG_PATH = os.getenv("NGINX_CONFIG_PATH")

class SiteService:
    def __init__(self, db: Session):
        self.db = db
        try:
            self.docker = docker.from_env()
        except Exception as e:
            print(f"CRITICAL: Could not connect to Docker socket: {e}")

    def create_site(self, site_data: SiteCreate) -> Site:
        existing = self.db.query(Site).filter(Site.slug == site_data.slug).first()
        if existing:
            raise HTTPException(status_code=400, detail="Slug already exists")

        site = Site(**site_data.model_dump())
        self.db.add(site)
        self.db.commit()
        self.db.refresh(site)
        return site

    def update_or_create_nginx_config(self, config_data: NginxConfigCreate) -> NginxSiteConfig:
        config = self.db.query(NginxSiteConfig).options(
            joinedload(NginxSiteConfig.site)
        ).filter(NginxSiteConfig.site_id == config_data.site_id).first()

        if config:
            config.port = config_data.port
            config.extra_config = config_data.extra_config
        else:
            config = NginxSiteConfig(**config_data.model_dump())
            self.db.add(config)

        self.db.commit()
        self.db.refresh(config)
        return config

    def get_sites(self):
        return self.db.query(Site).all()

    def get_site_or_404(self, site_id: str) -> Site:
        site = self.db.query(Site).filter(Site.id == site_id).first()
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        return site

    def trigger_build(self, site_id: str, background_tasks):
        site = self.get_site_or_404(site_id)

        site.status = "building"
        self.db.commit()

        manager = BuildManager(self.db, self.docker)
        background_tasks.add_task(manager.run_build, site_id)

        return {"message": "Build started", "site_slug": site.slug}

    def generate_nginx_file_and_reload(self, site_id: str):
        site = self.get_site_or_404(site_id)
        file_path=""
        try:
            file_path = generate_nginx_file(site, NGINX_CONFIG_PATH)
            self.reload_nginx_container()
            print(f"Success: {file_path}")
        except Exception as e:
            print(f"Error: {e}")

        return {"message": "Generated and reload nginx", "site_slug": site.slug, "file_path": file_path}

    def reload_nginx_container(self):

        try:
            container = self.docker.containers.get("nginx-sites")
            container.exec_run("nginx -s reload")
            print("Nginx reloaded successfully")
        except Exception as e:
            print(f"Failed to reload Nginx: {e}")

    def get_logs(self, site_id: str):
        return (
            self.db.query(BuildLog)
            .filter(BuildLog.site_id == site_id)
            .order_by(BuildLog.started_at.desc())
            .all()
        )