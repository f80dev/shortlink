#docker build -t f80hub/shortlinks .
#docker push f80hub/shortlinks:latest
#docker rm -f shortlinks && docker run --name shortlinks -ti f80hub/shortlinks:latest

#FROM python:3.13.0a3-alpine3.18
#RUN apk add py3-gunicorn
#RUN apk add py3-flask
#RUN apk add py3-pip
#RUN ask add --no-cache python3-pymongo

FROM python:latest

# installation requirements
COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY *.py .

ENV PORT=80
EXPOSE 80

# Set working directory and start app
CMD ["gunicorn", "--bind", "0.0.0.0:80", "wsgi:app"]
