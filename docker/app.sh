#!/bin/bash
# app.sh — start-up script for the web application container.
# It runs every time the "booking" container starts.

# 1) Apply any pending database migrations so the schema is up to date.
#    "upgrade head" means: bring the DB to the latest migration version.
alembic upgrade head

# 2) Start the production web server (gunicorn) which runs our FastAPI app.
#    --workers 4                                    : 4 parallel worker processes
#    --worker-class uvicorn.workers.UvicornWorker   : run async FastAPI correctly
#    --bind=0.0.0.0:8000                            : listen on port 8000 in the container
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
