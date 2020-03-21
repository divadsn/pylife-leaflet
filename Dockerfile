FROM python:3.6
LABEL maintainer="David Sn <divad.nnamtdeis@gmail.com>"
ADD . /app
RUN pip install -r /app/requirements.txt
ENTRYPOINT [ "python", "/app/run.py" ]