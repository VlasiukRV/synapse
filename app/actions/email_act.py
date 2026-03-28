import smtplib
import os
import logging
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader

from app.actions.base import BaseAction

logger = logging.getLogger("uvicorn.error")
env = Environment(loader=FileSystemLoader('/app/templates'))

class EmailAction(BaseAction):
    async def execute(self, data: dict, params: dict) -> dict:

        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASSWORD")

        from_email = os.getenv("EMAIL_FROM", smtp_user)
        to_email = params.get("to", from_email)
        subject = params.get("subject", "New Synapse Lead")

        template_name = params.get("template", "base_email.html")
        template = env.get_template(template_name)

        html_content = template.render(
            data=data,
            form_name=params.get("subject", "Form"),
            # logo_url=selected_brand["logo"],
            # brand_class=selected_brand["class"],
            # company_name=selected_brand["name"],
            year=date.today().year
        )

        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        customer_email = data.get("email")
        if customer_email:
            msg['Reply-To'] = customer_email
        msg.attach(MIMEText(html_content, 'html'))

        try:

            server = smtplib.SMTP(smtp_host, smtp_port, timeout=15)
            logger.info(f"Connecting to {smtp_host}:{smtp_port}...")

            server.set_debuglevel(1)
            server.connect(smtp_host, smtp_port)

            server.starttls()

            server.login(smtp_user, smtp_pass)
            server.sendmail(
                from_email,
                [to_email],
                msg.as_string().encode('utf-8')
            )

            server.quit()

            logger.info(f"Email sent successfully to {to_email}")
            return {"status": "success", "action": "email_send", "recipient": to_email}

        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return {"status": "error", "message": str(e)}