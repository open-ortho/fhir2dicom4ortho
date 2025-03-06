""" Invoke tasks for building and pushing the Docker image to the private registry. 

This is the equivalent of a Makefile. It is used to automate the process of building and pushing the Docker image to the private registry.
"""
import toml
from invoke import task
import time

# Load the version from pyproject.toml
with open("pyproject.toml", "r") as f:
    pyproject = toml.load(f)
    version = pyproject["project"]["version"]
    project_name = pyproject["project"]["name"]
    organization = pyproject["tool"]["organization"]["name"]

registry = "cr.medoco.health"
docker_image_name = f"{registry}/{organization}/{project_name}"

@task
def export_requirements(c):
    """Export dependencies to requirements.txt."""
    c.run("poetry export -f requirements.txt --output requirements.txt --without-hashes")

@task(pre=[export_requirements])
def build(c):
    """Build the Docker image."""
    c.run(f"docker build --platform linux/amd64 -t {docker_image_name}:latest -t {docker_image_name}:{version} .")

@task
def push(c):
    """Push the Docker image to the private registry."""
    c.run(f"docker push {docker_image_name}:latest")
    c.run(f"docker push {docker_image_name}:{version}")

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
    print(f"Docker image built and pushed to the private registry with tags 'latest' and '{version}'.")
