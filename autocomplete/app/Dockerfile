FROM python:3.8
LABEL maintainer "Brian Walsh <walsbr@ohsu.edu>"
WORKDIR /app
COPY requirements.txt /
RUN pip install -r /requirements.txt
COPY ./ ./
EXPOSE 8050
CMD ["python", "-m" "app_autocomplete"]
