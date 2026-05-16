from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class SiteCreate(BaseModel):
    slug: str
    domain: str
    template_path: str
    output_path: str

class SiteResponse(BaseModel):
    id: str
    slug: str
    status: str
    last_build_at: Optional[datetime]
    template_path: str

    class Config:
        from_attributes = True

class BuildLogResponse(BaseModel):
    id: str
    site_id: str
    success: bool
    started_at: datetime
    log_output: Optional[str]

    class Config:
        from_attributes = True

class NginxConfigBase(BaseModel):
    port: int
    extra_config: Optional[str] = None

class NginxConfigCreate(NginxConfigBase):
    site_id: str

class NginxConfigResponse(NginxConfigBase):
    id: UUID
    site_id: str

    class Config:
        from_attributes = True