# TODO 1: Base image Python resmi yang ringan (varian slim).
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
# TODO 2: Install dependency dari requirements.txt.
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# TODO 3: Perintah default saat container start (mode dengan lock).
CMD ["python3", "src/order_simulator.py"]
