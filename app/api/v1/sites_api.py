from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from typing import List

from app.schemas.sites_schemas import SiteCreate, SiteResponse, BuildLogResponse, NginxConfigResponse, NginxConfigCreate
from app.dependencies.sites_dependencies import get_site_service
from app.services.site_service import SiteService

router = APIRouter()


@router.post("/", response_model=SiteResponse)
def create_site(
    site_data: SiteCreate,
    service: SiteService = Depends(get_site_service)
):
    return service.create_site(site_data)


@router.get("/", response_model=List[SiteResponse])
def get_sites(
        service: SiteService = Depends(get_site_service)
):
    return service.get_sites()


@router.post("/{site_id}/build")
def trigger_build(
    site_id: str,
    background_tasks: BackgroundTasks,
    service: SiteService = Depends(get_site_service)
):

    res = service.trigger_build(site_id, background_tasks)
    background_tasks.add_task(service.generate_nginx_file_and_reload, site_id)

    return res


@router.get("/{site_id}/logs", response_model=List[BuildLogResponse])
def get_site_logs(
    site_id: str,
    service: SiteService = Depends(get_site_service)
):
    return service.get_logs(site_id)


@router.get("/{site_id}/nginx", response_model=NginxConfigResponse)
def get_nginx_config(
        site_id: str,
        service: SiteService = Depends(get_site_service)
):
    site = service.get_site_or_404(site_id)
    if not site.nginx_config:
        raise HTTPException(status_code=404, detail="Nginx config not found for this site")
    return site.nginx_config


@router.post("/nginx", response_model=NginxConfigResponse)
def save_nginx_config(
        config_data: NginxConfigCreate,
        background_tasks: BackgroundTasks,
        service: SiteService = Depends(get_site_service)
):
    config = service.update_or_create_nginx_config(config_data)

    background_tasks.add_task(service.generate_nginx_file_and_reload, config_data.site_id)

    return config