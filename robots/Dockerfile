FROM python:3.9-slim

# Create working directory
RUN mkdir -p /robots && \
    chown -R 777 /robots

WORKDIR /robots

# Copy only requirements first for better caching
COPY requirements.txt . 

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

CMD tail -f /dev/null
