FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY fastapi/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN git config --global user.email "system@mdar.internal" \
    && git config --global user.name "MDAR System" \
    && git config --global safe.directory '*'
RUN mkdir -p /app/file_cloud

COPY fastapi/ .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
