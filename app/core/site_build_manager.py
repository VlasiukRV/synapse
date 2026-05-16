import os
from dotenv import load_dotenv
import docker

from datetime import datetime
from sqlalchemy.orm import Session
from app.models.sites_models import Site, BuildLog

load_dotenv()
class BuildManager:
    def __init__(self, db: Session, docker):
        self.db = db
        self.docker = docker
        self.host_project_path = os.getenv("HOST_PROJECT_PATH")
        if not self.host_project_path:
            print("WARNING: HOST_PROJECT_PATH is not set in .env")

    def run_build(self, site_id: str):
        site = self.db.query(Site).filter(Site.id == site_id).first()
        if not site:
            return {"error": "Site not found"}

        if not self.host_project_path:
            return {"error": "HOST_PROJECT_PATH is missing in .env or not loaded"}

        build_log = BuildLog(site_id=site.id)
        self.db.add(build_log)
        self.db.commit()

        full_output = []

        host_template_path = site.template_path.replace("/app", self.host_project_path)
        # host_output_path = site.output_path.replace("/app", self.host_project_path)

        try:

            container = self.docker.containers.run(
                image="node:22-slim",
                command='sh -c "rm -rf .astro package-lock.json node_modules/* node_modules/.* 2>/dev/null; npm install --legacy-peer-deps && npm run build"',
                working_dir="/app",
                environment={
                    "SITE_NAME": site.slug
                },
                volumes={
                    self.host_project_path: {'bind': '/app', 'mode': 'rw'},
                    'synapse_node_modules': {'bind': '/app/node_modules', 'mode': 'rw'}
                },
                detach=True,
                remove=True,
                name=f"debug-{site.slug}"
            )

            for line in container.logs(stream=True):
                decoded_line = line.decode('utf-8')
                full_output.append(decoded_line)

            build_log.success = True
            site.last_build_at = datetime.utcnow()

        except Exception as e:
            build_log.success = False
            full_output.append(f"BUILD FAILED: {str(e)}")

        finally:
            build_log.log_output = "".join(full_output)
            self.db.commit()

        return {"status": "success" if build_log.success else "failed", "log_id": build_log.id}