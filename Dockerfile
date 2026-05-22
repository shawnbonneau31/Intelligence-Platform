FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Initialize database and seed data
RUN python seed_data.py

EXPOSE 8080

ENV PORT=8080
ENV NAMARA_SECRET=change-this-in-production

CMD ["python", "server.py"]
