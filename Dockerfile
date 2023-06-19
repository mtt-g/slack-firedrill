# Use an official Python runtime as the base image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the project files to the working directory
COPY . /app

# Install project dependencies
RUN pip install --no-cache-dir pyyaml slack_bolt

# Run the Python script
CMD ["python", "app.py"]