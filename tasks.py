""" Invoke tasks for building and pushing the Docker image to the private registry. 

This is the equivalent of a Makefile. It is used to automate the process of
building and pushing the Docker image to the private registry.
"""
import time

import toml
from invoke import task

# Load the version from pyproject.toml
with open("pyproject.toml", "r", encoding='utf-8') as f:
    pyproject = toml.load(f)
    version = pyproject["project"]["version"]
    project_name = pyproject["project"]["name"]
    organization = pyproject["tool"]["organization"]["name"]

REGISTRY = "cr.medoco.health"
DOCKER_IMAGE_NAME = f"{REGISTRY}/{organization}/{project_name}"


@task
def export_requirements(c):
    """Export dependencies to requirements.txt."""
    c.run("poetry export -f requirements.txt --output requirements.txt --without-hashes")


@task(pre=[export_requirements])
def build(c):
    """Build the Docker image."""
    c.run(
        f"docker build -t {DOCKER_IMAGE_NAME}:latest -t {DOCKER_IMAGE_NAME}:{version} .")


@task
def push(c):
    """Push the Docker image to the private registry."""
    c.run(f"docker push {DOCKER_IMAGE_NAME}:latest")
    c.run(f"docker push {DOCKER_IMAGE_NAME}:{version}")


@task
def ensure_orthanc_running(c):
    """Ensure the Orthanc service is running."""
    c.run("docker compose -f test/docker-compose.yml up -d")
    time.sleep(2)  # Wait for Orthanc to start


@task(pre=[export_requirements, ensure_orthanc_running])
def test(c):
    """Run all unit tests."""
    # Set up environment variables for testing and run tests. Its crazy: these are set in the test code as well!
    c.run("""
        set -a
        source test/env-dev
        set +a
        python -m unittest -v
    """, pty=True)


@task(pre=[test, build, push])
def deploy(c):
    """Build and push the Docker image."""
    print(
        f"Docker image built and pushed to the private registry with tags 'latest' and '{version}'.")
