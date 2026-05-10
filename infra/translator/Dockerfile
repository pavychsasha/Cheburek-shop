FROM python:3.12-alpine

WORKDIR /service
COPY server.py /service/server.py

ENV TRANSLATOR_HOST=0.0.0.0
ENV TRANSLATOR_PORT=5000

EXPOSE 5000

CMD ["python", "/service/server.py"]
