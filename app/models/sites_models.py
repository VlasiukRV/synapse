import os
import uuid
from sqlalchemy import func, Column, String, DateTime, ForeignKey, Boolean, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from app.database import Base

class Site(Base):
    __tablename__ = "sites"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    slug = Column(String, unique=True, index=True) # client-a
    domain = Column(String)
    template_path = Column(String) # /app/templates/default-blog
    output_path = Column(String)   # /app/storage/client-a
    status = Column(String, default="active")
    last_build_at = Column(DateTime, nullable=True)

    nginx_config = relationship("NginxSiteConfig", back_populates="site", uselist=False)


class NginxSiteConfig(Base):
    __tablename__ = "nginx_site_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(String, ForeignKey("sites.id"), unique=True)

    port = Column(Integer, nullable=False)

    extra_config = Column(Text, nullable=True)

    # Зв'язок з основною таблицею Site
    site = relationship("Site", back_populates="nginx_config")

    @hybrid_property
    def full_root_path(self):
        base_path = "/var/www/html/"
        if self.site and self.site.output_path:
            folder_name = os.path.basename(self.site.output_path.rstrip('/'))
            return f"{base_path}{folder_name}"
        return base_path

    @full_root_path.expression
    def full_root_path(cls):

        base_path = "/var/www/html/"
        return func.concat(
            base_path,
            func.reverse(func.split_part(func.reverse(Site.output_path), '/', 1))
        )

class SiteConfig(Base):
    __tablename__ = "site_configs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(String, ForeignKey("sites.id"))
    key = Column(String)
    value = Column(JSON)

class BuildLog(Base):
    __tablename__ = "build_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(String, ForeignKey("sites.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    success = Column(Boolean, default=False)
    log_output = Column(Text)