# Start with an official Python base image.
FROM python:3.12-slim

# Install Tkinter dependencies AND a compatibility library for WSLg
RUN apt-get update && apt-get install -y tk libxcb-cursor0

# Set the working directory inside the container.
WORKDIR /app

# Copy the requirements file into the container.
COPY requirements.txt .

# Install the Python dependencies.
RUN sed '/pywin32-ctypes/d' requirements.txt | pip install --no-cache-dir -r /dev/stdin

# Copy your application's source code and resources into the container.
COPY source/ ./source/
COPY resources/ ./resources/

# Tell the container what command to run when it starts.
CMD ["python", "source/main.py"]