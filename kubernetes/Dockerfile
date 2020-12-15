FROM python:3.7.9-slim

# Both items are required
RUN apt-get update -y
RUN apt-get install postgresql -y postgresql-contrib

# Copy all files into the docker dir
# Copy all core files into docker dir
COPY ./screaper /app/screaper
COPY ./requirements.txt /app/requirements.txt

# COPY . /app
ENV HOME=/app
WORKDIR /app

# Install Python web server and dependencies
RUN pip install -r ./requirements.txt

# Expose port
EXPOSE 5000
EXPOSE 80
EXPOSE 8080

# Run a single python application

CMD ["python", "-m", "screaper.run"]
