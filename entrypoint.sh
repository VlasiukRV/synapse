#!/bin/bash
set -e

if [ -e /var/run/docker.sock ]; then

    chmod 666 /var/run/docker.sock || true

    G_ID=$(stat -c "%g" /var/run/docker.sock)

    if [ "$G_ID" != "0" ]; then
        groupadd -g "$G_ID" docker_host || true
        usermod -aG docker_host synapse || true
    else
        usermod -aG root synapse || true
    fi
fi

chown -R synapse:synapse /app/data || true

exec gosu synapse uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload