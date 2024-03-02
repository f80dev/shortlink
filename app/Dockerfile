#docker build -t f80hub/shortlinks .
#docker push f80hub/shortlinks:latest
#docker rm -f shortlinks && docker pull f80hub/shortlinks && docker run --name shortlinks -p 80:80 -p 5000:5000 -ti f80hub/shortlinks:latest
#test sur serveur :
#docker rm -f shortlinks && docker pull f80hub/shortlinks && docker run --name shortlinks -p 443:443 -e PORT=443 -ti f80hub/shortlinks:latest
#docker rm -f shortlinks && docker pull f80hub/shortlinks && docker run --name shortlinks -p 80:80 -e PORT=80 -ti f80hub/shortlinks:latest

FROM python:3.13.0a3-alpine3.18
RUN apk add py3-gunicorn
RUN apk add py3-flask
RUN apk add py3-pip
RUN apk add py3-openssl


#RUN ask add --no-cache python3-pymongo

#FROM python:latest

# installation requirements
RUN pip3 install --upgrade pip
RUN pip3 install -v pymongo
RUN pip3 install -v Flask
RUN pip3 install -v Flask-Cors
RUN pip3 install -v gunicorn
RUN pip3 install -v pyyaml

#RUN pip3 install -v pyopenssl

#COPY requirements.txt .
#RUN pip3 install -r requirements.txt

RUN mkdir static

COPY *.py .
COPY ./static/* /static
COPY f80.fr_ssl_certificate.cer ./cert.pem
COPY _.f80.fr_private_key.pem ./key.pem

EXPOSE 80
EXPOSE 5000


# Set working directory and start app
#voir https://blog.miguelgrinberg.com/post/running-your-flask-application-over-https pour l'usage de gunicorn avec les certificat
#CMD ["gunicorn", "--certfile","cert.pem","--keyfile","key.pem", "--bind", "0.0.0.0:80", "wsgi:app"]
#CMD ["gunicorn", "--bind", "0.0.0.0:80", "wsgi:app"]
#CMD ["gunicorn", "--bind", "0.0.0.0:5000", "wsgi:app"]
CMD ["python", "app.py","cloud"]
#CMD ["python", "app.py","80"]
