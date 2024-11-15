from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, expr, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType


# Initialize Spark session
spark = SparkSession.builder \
    .appName("ECommerceOrdersPaymentsStreaming") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-token-provider-kafka-0-10_2.12:3.5.0,org.mongodb.spark:mongo-spark-connector_2.12:10.3.0") \
    .config("spark.sql.shuffle.partitions", "5") \
    .config("spark.streaming.backpressure.enabled", "true") \
    .config("spark.streaming.stopGracefullyOnShutdown", "true") \
    .config("spark.streaming.kafka.maxRatePerPartition", "10") \
    .config("spark.default.parallelism", "5") \
    .getOrCreate()

# Define the order and payment schemas
order_schema = StructType([
    StructField("order_id", StringType(), True),
    StructField("order_date", TimestampType(), True),
    StructField("created_at", TimestampType(), True),
    StructField("customer_id", StringType(), True),
    StructField("amount", IntegerType(), True)
])

payment_schema = StructType([
    StructField("payment_id", StringType(), True),
    StructField("order_id", StringType(), True),
    StructField("payment_date", TimestampType(), True),
    StructField("created_at", TimestampType(), True),
    StructField("amount", IntegerType(), True)
])

kafka_config = {
    "kafka.bootstrap.servers":"localhost:9092",
    # "kafka.security.protocol":"SASL_SSL",
    # "kafka.sasl.mechanism":"PLAIN",
    # "kafka.sasl.jaas.config":"org.apache.kafka.common.security.plain.PlainLoginModule required username='***' password='**';",
    "startingOffsets":"latest"
}

orders_data_topic = "orders"
payments_data_topic = "payments"

mongo_config = {
    "spark.mongodb.connection.uri":"mongodb://admin:password@127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.2",
    "spark.mongodb.database":"ecomm_mart",
    "spark.mongodb.collection":"validated_orders"    
}


# Read orders from Kafka
orders_df = spark \
    .readStream \
    .format("kafka") \
    .options(**kafka_config) \
    .option("subscribe", orders_data_topic) \
    .load() \
    .selectExpr("CAST(value AS STRING) as value") \
    .select(from_json(col("value"), order_schema).alias("data")) \
    .select("data.*") \
    .withWatermark("order_date", "10 minutes")\
    .repartition(5)
print("Orders stream read")

# Read payments from Kafka
payments_df = spark \
    .readStream \
    .format("kafka") \
    .options(**kafka_config) \
    .option("subscribe", payments_data_topic) \
    .load() \
    .selectExpr("CAST(value AS STRING) as value") \
    .select(from_json(col("value"), payment_schema).alias("data")) \
    .select("data.*") \
    .withWatermark("payment_date", "10 minutes")\
    .repartition(5)
print("Payments stream read")

# Join orders and payments on order_id with 30 minutes window
joined_df = orders_df.alias("orders").join(
    payments_df.alias("payments"),
    expr("""
        orders.order_id = payments.order_id AND
        payments.payment_date BETWEEN orders.order_date AND
        orders.order_date + interval 1 minutes AND payments.amount = orders.amount
    """),
    "inner"
).select(
    col("orders.order_id"),
    col("orders.order_date"),
    col("orders.created_at").alias("order_created_at"),
    col("orders.customer_id"),
    col("orders.amount").alias("order_amount"),
    col("payments.payment_id"),
    col("payments.payment_date"),
    col("payments.created_at").alias("payment_created_at"),
    col("payments.amount").alias("payment_amount")
).repartition(5)

#Write completed orders to MongoDB
query = joined_df.writeStream \
    .outputMode("append") \
    .format("mongodb") \
    .option("checkpointLocation", "./temp_data/mongo_db_checkpoint11") \
    .options(**mongo_config) \
    .option("truncate", False) \
    .start()
    
print("Write successfull")

query.awaitTermination()