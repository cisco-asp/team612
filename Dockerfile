FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY publish_message.py .
COPY connect_pyats.py .
COPY connect_netmiko.py .
COPY render_config.py .

EXPOSE 5000

CMD ["python", "app.py"]