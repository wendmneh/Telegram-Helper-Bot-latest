# Use official Python image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app


# # Install system dependencies (minimal)
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     && rm -rf /var/lib/apt/lists/*


# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .


# Command to run your bot (replace bot.py with your main file)
CMD ["python", "Telegram_Bot.py"]

python Telegram_Bot.py




