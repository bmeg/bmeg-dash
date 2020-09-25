FROM python:3.8
LABEL maintainer "Brian Walsh <walsbr@ohsu.edu>"
# ensure OpenSSL installed
RUN    apt-get update \
    && apt-get install openssl \
    && apt-get install ca-certificates

# base working dir `/app`
WORKDIR /app
# install python dependencies
COPY requirements.txt /
RUN pip install -r /requirements.txt
# install app
COPY ./bmeg_app ./bmeg_app
COPY ./bin ./bin
# start app
EXPOSE 8050
CMD ["python", "-m", "bmeg_app"]
