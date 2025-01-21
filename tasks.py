import toml
from invoke import task

# Load the version from pyproject.toml
with open("pyproject.toml", "r") as f:
    pyproject = toml.load(f)
    version = pyproject["project"]["version"]
    project_name = pyproject["project"]["name"]
    organization = pyproject["tool"]["organization"]["name"]

registry = "cr.medoco.health"
docker_image_name = f"{registry}/{organization}/{project_name}"

@task
def build(c):
    """Build the Docker image."""
    c.run(f"docker build -t {docker_image_name}:latest -t {docker_image_name}:{version} .")

@task
def push(c):
    """Push the Docker image to the private registry."""
    c.run(f"docker push {docker_image_name}:latest")
    c.run(f"docker push {docker_image_name}:{version}")

@task(pre=[build, push])
def deploy(c):
    """Build and push the Docker image."""
    print(f"Docker image built and pushed to the private registry with tags 'latest' and '{version}'.")