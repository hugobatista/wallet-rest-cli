---
description: 'CLI coding conventions for the project.'
---

# Docker
- if implementing a CLI, make sure to provide a Dockerfile for easy deployment and usage. The Dockerfile should include instructions for building the CLI application and installing any necessary dependencies. This will allow users to run the CLI in a containerized environment without having to worry about setting up the environment or installing dependencies manually.

An example Dockerfile for a Python CLI application might look like this (replace `appname` with the actual name of your CLI application):

```Dockerfile
FROM python:3.12-slim

# Links Docker image with repository
LABEL org.opencontainers.image.source=https://go.hugobatista.com/gh/appname
LABEL security.scan="true"
LABEL maintainer="Hugo Batista <mail@hugobatista.com>"


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_ROOT_USER_ACTION=ignore

WORKDIR /app
COPY . /app

RUN pip install --no-cache --upgrade pip \
 && pip install --no-cache /app \
 && addgroup --system app && adduser --system --group app 

USER app

HEALTHCHECK --interval=300s --timeout=10s --start-period=5s --retries=3 \
    CMD appname --version || exit 1

ENTRYPOINT ["appname']

```

If creating the Dockerfile, make sure to also create a .dockerignore file to exclude unnecessary files and directories from the Docker build context. This will help reduce the size of the Docker image and speed up the build process. 
Make sure to update readme.md with instructions on how to use the dockerized version of the CLI, including how to build the Docker image and run the container. This will make it easier for users to get started with the CLI without having to worry about setting up the environment or installing dependencies manually. When using the dockerized version of the CLI, the user can pull the latest image from the GHCR registry (see the ghcr.yml file for details) and run the container with the appropriate environment variables and command-line arguments to access the CLI functionality.


# Pypi

The project will be published on Pypi. When writing or updating readme.md, make sure to include instructions on how to install the CLI using pip. 
