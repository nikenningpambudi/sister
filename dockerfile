FROM python:3.9-alphine
WORKDIR /app
COPY backend.py,frontend.py,stok_barang.py,reporting.py,web_app.py,web_app_report.py 
RUN 

COPY