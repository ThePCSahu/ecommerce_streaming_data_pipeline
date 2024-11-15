
# E-Commerce Orders & Payments Validation Streaming Data Pipeline

## Project Overview

This project implements a real-time streaming data pipeline for validating e-commerce orders and payments. The pipeline reads data from Kafka topics in Avro format, validates the payment amount against the order amount, and stores the validated data in MongoDB for further analysis and consumption.

### Key Features:
- **Real-time Streaming**: Processes order and payment streams from Kafka.
- **Validation Logic**: Validates if the payment amount matches the corresponding order amount.
- **Fault Tolerance**: Utilizes Spark's checkpointing mechanism.
- **Late Data Handling**: Configured watermarking time of 30 minutes to handle late data.
- **Scalability**: Can be used in production and non-production environments.

## Components

### 1. Mock Data Producer
- Publishes mock order and payment data to Kafka topics for testing and development.
- Designed for non-production environments.

### 2. E-Commerce Streaming App
- Reads data streams from Kafka.
- Validates payments against orders.
- Saves validated data (fact data) to MongoDB.

## Setup Instructions

### Prerequisites
- **Docker**: Ensure Docker is installed for running Kafka and MongoDB containers.
- **Python Environment**: Set up a Python environment with the required packages.

### Steps to Set Up

1. **Spin up Kafka and MongoDB Containers**  
   Use the provided Docker Compose file to start the necessary containers:
   ```bash
   docker compose up -d
   ```

2. **Install Required Python Packages**  
   Install Spark and Kafka dependencies:
   ```bash
   pip install pyspark==3.5.0 confluent-kafka
   ```

3. **Configure Kafka and MongoDB Credentials**  
   Update the configuration in the `E-Commerce Streaming App` to connect to Kafka and MongoDB.

4. **Login to Kafka Control Center**  
   Kafka Control Center allows you to manage Kafka topics and monitor streams.
   - Navigate to [http://localhost:9021](http://localhost:9021).
   - Use the default credentials (or as configured in Docker Compose):
     - **Username**: admin  
     - **Password**: password  

5. **Create Kafka Topics**  
   Use Kafka Control Center to create the necessary topics:
   - **orders**: For order data.
   - **payments**: For payment data.
   
   **Configuration**:
   - Set **Partitions** to 3 (or more for higher parallelism).
   - Optionally enable **Log Compaction** for deduplication.

6. **Set Up MongoDB Database and Collection**  
   Access MongoDB and create the database and collection:
   ```bash
   docker exec -it <mongodb_container_name> mongosh
   ```
   ```javascript
   use ecomm_mart; // Create or switch to database
   db.createCollection("validated_orders");
   show collections; // Verify the collection
   ```

7. **Start the Mock Data Producer**  
   Publish mock data to Kafka topics:
   ```bash
   python mock_data_producer.py
   ```

8. **Start the E-Commerce Streaming App**  
   Run the streaming application:
   ```bash
   python ecomm_streaming_app.py
   ```

### Technical Configuration

#### Kafka Configuration in `ecomm_streaming_app.py`
Ensure the app connects to the correct Kafka topics:
```python
kafka_brokers = "localhost:9092"
order_topic = "orders"
payment_topic = "payments"
```

#### MongoDB Configuration in `ecomm_streaming_app.py`
Ensure MongoDB integration:
```python
from pymongo import MongoClient

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client.ecomm_db
validated_collection = db.validated_transactions
```

---

## Technical Details

### Watermarking
- Configured to handle late data with a **10-minute watermark**. Ensures that events arriving within 30 minutes are still processed correctly.

### Fault Tolerance
- **Checkpointing** is implemented to recover from failures and ensure data consistency.

### Data Flow
1. **Order and Payment Streams** are consumed from Kafka topics.
2. **Validation Logic** checks if the payment amount matches the order amount.
3. **Validated Records** are saved to MongoDB for downstream consumption.

---

## Conclusion

This pipeline ensures robust and real-time validation of e-commerce transactions, providing a reliable data stream for analysis and reporting. It can be seamlessly integrated into production systems and scaled for high-throughput environments.
