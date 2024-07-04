# Use an official Python runtime as a parent image
FROM python:3.6

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /mapping

# Copy the current directory contents into the container at /app
COPY . /mapping/

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

# Expose port 8000 to the outside world
EXPOSE 8000

# Define the command to run your application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]