Integration tests instructions for Service Clients

Prerequisites:
- Service running locally (uvicorn) e.g. http://localhost:8000
- RabbitMQ reachable (RABBITMQ_URL)
- Python 3.10+ virtualenv

Install deps:

pip install httpx aio-pika

Run:

python integration_create_customer_and_listen.py

Environment variables (optional):
- CLIENTS_API_URL, RABBITMQ_URL, RABBITMQ_EXCHANGE, EVENT_TIMEOUT

Notes:
- The script creates a customer and listens for the `customer.created` event on exchange `mspr.events`.
- If RabbitMQ is unavailable, the create request may still succeed but no event will be received.
