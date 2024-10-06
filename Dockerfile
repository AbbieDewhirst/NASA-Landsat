# Use the official Python image with the specified version
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Install Poetry
RUN pip install poetry

# Install dependencies
RUN poetry install

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application
CMD ["poetry", "run", "python", "landsat_webapp/app.py"]
