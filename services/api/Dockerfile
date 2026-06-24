FROM python:3.12-slim

WORKDIR /app
COPY app.py /app/app.py

RUN useradd --create-home --shell /usr/sbin/nologin appuser
USER appuser

EXPOSE 8000
CMD ["python", "app.py"]
