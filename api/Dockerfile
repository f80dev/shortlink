#docker build -t f80hub/shortlinks .
#docker push f80hub/shortlinks:latest

FROM python:3.13.0a3-alpine3.18

# Copy application code
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY . .

# Expose Flask port
EXPOSE 5000

# Set working directory and start app
WORKDIR /app
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
