
# E-Commerce Orders & Payments Validation Streaming Pipeline

## Tech Stack

- **Kafka**: Message broker for real-time data streaming.
- **Spark Streaming**: Real-time data processing.
- **MongoDB**: NoSQL database for storing validated data.
- **Python**: Programming language for implementing the streaming application.
- **Docker**: Containerization platform for running Kafka and MongoDB.

## Overview

This project implements a real-time streaming pipeline for validating e-commerce orders and payments. It processes data from Kafka topics, validates payment amounts, and stores validated records in MongoDB.

### Key Features:
- **Validation**: Ensures payment matches the order amount.
- **Real-time Streaming**: Processes orders and payments from Kafka.
- **Fault Tolerance**: Uses Spark checkpointing for reliability.
- **Late Data Handling**: Configured with a 10-minute watermark.

## Components

- **Mock Data Producer**: Simulates order and payment data for testing.
- **E-Commerce Streaming App**: Consumes data from Kafka, validates payments, and stores validated data in MongoDB.



## System Diagram
This diagram illustrates the architecture and data flow of the ecommerce orders & payments validation streaming pipeline, showing the key components and their interactions.

```
               +-----------------------+
               |   Mock Data Producer  |
               |   (Simulates Orders   |
               |   and Payments)       |
               +-----------------------+
                          |
                          v
               +--------------------- -+
               |        Kafka          |
               |   (Message Broker)    |
               |   +---------------+   |
               |   | Orders Topic  |   |
               |   +---------------+   |
               |   | Payments Topic|   |
               |   +---------------+   |
               +-----------------------+
                         |
                         v
               +-----------------------+
               |   Spark Streaming     |
               |   (Processes Orders   |
               |   and Payments)       |
               +-----------------------+
                         |
                         v
               +-----------------------+
               |       MongoDB         |
               |   +---------------+   |
               |   |   ecomm_mart  |   |
               |   |   (Database)  |   |
               |   | +-----------+ |   |
               |   | | validated | |   |
               |   | | _orders   | |   |
               |   | | Collection| |   |
               |   | +-----------+ |   |
               |   +---------------+   |
               +-----------------------+
```

## Setup

### Setup Steps

1. **Start Kafka and MongoDB Containers**  
   ```bash
   docker compose up -d
   ```

2. **Install Dependencies**  
   ```bash
   pip install pyspark==3.5.0 confluent-kafka
   ```

3. **Configure Kafka and MongoDB**  
   Update connection settings in the streaming app.

4. **Login to Kafka Control Center**  
   Access at [http://localhost:9021](http://localhost:9021) with default credentials:
   - **Username**: admin  
   - **Password**: password

5. **Create Kafka Topics**  
   Create `orders` and `payments` topics with 3+ partitions.

6. **Set Up MongoDB**  
   Create the database and collection:
   ```bash
   docker exec -it <mongodb_container_name> mongosh
   ```
   ```javascript
   use ecomm_mart;
   db.createCollection("validated_orders");
   ```

7. **Start Mock Data Producer**  
   ```bash
   python mock_data_producer.py
   ```

8. **Run Streaming App**  
   ```bash
   python ecomm_streaming_app.py
   ```

## Technical Configuration

### Kafka Setup
```python
kafka_brokers = "localhost:9092"
order_topic = "orders"
payment_topic = "payments"
```

### MongoDB Setup
```python
from pymongo import MongoClient

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client.ecomm_mart
validated_collection = db.validated_orders
```

## Technical Details

- **Watermarking**: 10-minute watermark for handling late data.
- **Fault Tolerance**: Checkpointing for recovery and data consistency.

### Data Flow
1. Consume Orders and Payments from Kafka.
2. Validate Payments against Orders.
3. Store Validated Data in MongoDB.

## Conclusion

This pipeline ensures reliable, real-time validation of e-commerce transactions, supporting data consistency and scalability.
