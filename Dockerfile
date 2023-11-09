# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Set the timezone environment variable
ENV TZ=Asia/Kolkata

# Install any needed packages specified in requirements.txt
# This assumes you have a requirements.txt with the necessary modules.
# E.g., requests, pytz. If not, replace this with a `RUN pip install` command.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Run script.py when the container launches
CMD ["python", "./script.py"]
