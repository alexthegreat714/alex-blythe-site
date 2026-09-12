FROM python:3.12-slim

WORKDIR /srv
COPY services/conversation/server.py /srv/server.py
USER 10001:10001
EXPOSE 5320
CMD ["python", "-u", "/srv/server.py"]
