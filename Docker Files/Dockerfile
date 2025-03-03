FROM python:3.12.4

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies for Playwright, rclone, curl, and others
RUN apt-get update && apt-get install -y \
	unzip \
    curl \
    gnupg2 \
    lsb-release \
    fuse \
    && rm -rf /var/lib/apt/lists/*

# Install rclone
RUN curl https://rclone.org/install.sh | bash

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright dependencies
RUN python -m playwright install --with-deps

#Install Playwright Chrome
RUN playwright install chrome

# Run the main script when the container starts
CMD ["python", "main.py"]
