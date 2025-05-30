FROM python:3-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app .
RUN chmod +x *.py

EXPOSE 5000

CMD ["python", "fs_db_wrap.py"]
