# Dockerfile — recipe for building the application image.
# Docker reads this file top-to-bottom and produces an "image":
# a frozen snapshot of an OS + Python + our code, ready to run anywhere.

# Base image: an official Linux that already has Python 3.11 installed.
FROM python:3.11

# Make Python behave nicely inside a container:
#   PYTHONUNBUFFERED=1      -> logs are printed immediately, not buffered.
#   PYTHONDONTWRITEBYTECODE -> do not litter the image with .pyc cache files.
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create the folder where our app will live inside the container...
RUN mkdir /booking

# ...and make it the default folder for all the commands below.
WORKDIR /booking

# Copy ONLY the dependency list first (before the rest of the code).
# This is a caching trick: as long as requirements.txt does not change,
# Docker reuses the cached "pip install" step and rebuilds much faster.
COPY requirements.txt .

# Install all Python libraries listed in requirements.txt.
# --no-cache-dir keeps the final image smaller.
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the project into the image.
COPY . .

# Make our helper start-up scripts executable.
RUN chmod a+x /booking/docker/*.sh

# Default command if the container is started without an explicit one.
# (docker-compose overrides this per service via "command:".)
# gunicorn is the production web server; it runs FastAPI through uvicorn workers.
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind=0.0.0.0:8000"]
