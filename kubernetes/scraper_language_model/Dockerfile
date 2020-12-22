FROM python:3.7.9-slim

# Install requirements
RUN apt-get update -y

COPY ./screaper_language_model /app/screaper_language_model
COPY ./kubernetes/scraper_language_model/requirements.txt /app/requirements.txt

ENV HOME=/app
WORKDIR /app

# Install Python web server and dependencies
RUN pip install -r ./requirements.txt

# Download the respective BERT mult models
RUN python -m deeppavlov install ner_ontonotes_bert_mult

# Actually, start the server
CMD ["python", "-m", "screaper_language_model.run"]

#ENTRYPOINT [
#    "gunicorn",
#    "-k", "gevent",
#    "-b", "0.0.0.0:8080",
#    "--timeout", "500",
#    "--workers", "1",
#    "screaper_language_model.run:application",
#    "--log-level", "debug"
#]
