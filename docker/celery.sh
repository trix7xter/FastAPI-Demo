#!/bin/bash
# celery.sh — start-up script shared by the "celery" and "flower" containers.
# The first argument ($1) decides which one to launch:
#   ./celery.sh celery  -> start a background-task worker
#   ./celery.sh flower  -> start the Flower monitoring dashboard

if [ "${1}" = "celery" ]; then
  # Worker: picks up and executes background tasks from the Redis queue.
  celery --app=app.tasks.celery:celery worker -l INFO
elif [ "${1}" = "flower" ]; then
  # Flower: web UI (port 5555) to watch task status and history.
  celery --app=app.tasks.celery:celery flower --port=5555 -l INFO
fi
