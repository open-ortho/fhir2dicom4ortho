# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the pyproject.toml and other necessary files to the container
COPY pyproject.toml README.md /app/

# Copy the rest of the application code to the container
COPY fhir2dicom4ortho /app/fhir2dicom4ortho
COPY pyproject.toml /app/

RUN pip install /app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["fhir2dicom4ortho"]