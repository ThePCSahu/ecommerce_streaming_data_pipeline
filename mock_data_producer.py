import json
import random
import time
from datetime import datetime, timedelta
from kafka import KafkaProducer

# Initialize Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    # security_protocol='SASL_SSL',
    # sasl_mechanism='PLAIN',
    # sasl_plain_username='***',
    # sasl_plain_password='***',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
orders_data_topic = "orders"
payments_data_topic = "payments"

# Generate sample data
def generate_order(order_id):
    return {
        "order_id": order_id,
        "order_date": datetime.now().isoformat(),
        "created_at": datetime.now().isoformat(),
        "customer_id": f"customer_{random.randint(1, 100)}",
        "amount": random.randint(100, 500)
    }

def generate_payment(order_id, payment_id, amount):
    return {
        "payment_id": payment_id,
        "order_id": order_id,
        "payment_date": (datetime.now() + timedelta(minutes=random.randint(1, 12))).isoformat(),
        "created_at": datetime.now().isoformat(),
        "amount": random.randint(amount-1, amount+2)
    }

# Send sample data to Kafka
order_ids = [f"order_{i}" for i in range(1, 1000)]
payment_ids = [f"payment_{i}" for i in range(1, 4)]

for order_id in order_ids:
    order = generate_order(order_id)
    producer.send(orders_data_topic, value=order)
    print(f"Sent order: {order}")

    # Send one or more payments for each order
    for payment_id in payment_ids:
        if random.choice([True, False]):  # Randomly decide if we send a payment for this order
            payment = generate_payment(order_id, payment_id, order['amount'])
            producer.send(payments_data_topic, value=payment)
            print(f"Sent payment: {payment}")
    
    time.sleep(1)  # Simulate delay between orders

producer.flush()
producer.close()