import json
import logging
from confluent_kafka import Consumer, Producer, KafkaException


BOOTSTRAP_SERVERS = "localhost:9092"

SOURCE_TOPIC = "ashpaz.order"
VALID_TOPIC = "ashpaz.valid"
ERROR_TOPIC = "ashpaz.error_log"

CONSUMER_GROUP_ID = "ashpaz-order-validator-group"


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


producer_config = {
    "bootstrap.servers": BOOTSTRAP_SERVERS
}

consumer_config = {
    "bootstrap.servers": BOOTSTRAP_SERVERS,
    "group.id": CONSUMER_GROUP_ID,
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False
}


producer = Producer(producer_config)
consumer = Consumer(consumer_config)


def delivery_report(err, msg):
    if err is not None:
        logging.error("Message delivery failed: %s", err)
    else:
        logging.info(
            "Message delivered to topic=%s partition=%s offset=%s",
            msg.topic(),
            msg.partition(),
            msg.offset()
        )


def validate_order(order):

    errors = []

    # -------------------------------
    # Rule 1: Phone Number Format
    # Phone number must start with +91 or 080
    # -------------------------------
    phone_number = order.get("phone_number", "")

    if not isinstance(phone_number, str):
        errors.append("INVALID_PHONE")
    elif not (phone_number.startswith("+91") or phone_number.startswith("080")):
        errors.append("INVALID_PHONE")

    # -------------------------------
    # Rule 2: Order Mode Conflict
    # request_online and request_table cannot both be true
    # -------------------------------
    request_online = order.get("request_online", False)
    request_table = order.get("request_table", False)

    if request_online and request_table:
        errors.append("ORDER_MODE_CONFLICT")

    # -------------------------------
    # Rule 3: Order Price Correctness
    # order_price == sum(unit_price * quantity)
    # -------------------------------
    items = order.get("items", [])
    calculated_total = 0

    try:
        for item in items:
            unit_price = item.get("unit_price", 0)
            quantity = item.get("quantity", 0)
            calculated_total += float(unit_price) * int(quantity)

        order_price = float(order.get("order_price", 0))

        if round(calculated_total, 2) != round(order_price, 2):
            errors.append("PRICE_MISMATCH")

    except Exception:
        errors.append("PRICE_MISMATCH")

    # -------------------------------
    # Return validation result
    # -------------------------------
    if len(errors) == 0:
        return True, None

    error_event = {
        "order_id": order.get("order_id", ""),
        "error_type": "MULTI" if len(errors) > 1 else errors[0],
        "error_reason": errors,
        "original_order": order
    }

    return False, error_event


def send_json(topic, data):
    producer.produce(
        topic=topic,
        value=json.dumps(data).encode("utf-8"),
        callback=delivery_report
    )

    producer.poll(0)


def process_message(raw_message):
    """
    Decode message, validate it, and route it.
    """

    try:
        order = json.loads(raw_message.decode("utf-8"))
    except json.JSONDecodeError:
        logging.error("Received invalid JSON message")

        error_event = {
            "order_id": "",
            "error_type": "INVALID_JSON",
            "error_reason": ["Message could not be parsed as valid JSON"],
            "original_order": raw_message.decode("utf-8", errors="replace")
        }

        send_json(ERROR_TOPIC, error_event)
        return

    is_valid, error_event = validate_order(order)

    if is_valid:
        send_json(VALID_TOPIC, order)

        logging.info(
            "VALID order routed to %s | order_id=%s",
            VALID_TOPIC,
            order.get("order_id")
        )

        print(f"Processed VALID order: {order.get('order_id')}")

    else:
        send_json(ERROR_TOPIC, error_event)

        logging.info(
            "INVALID order routed to %s | order_id=%s | errors=%s",
            ERROR_TOPIC,
            order.get("order_id"),
            error_event["error_reason"]
        )

        print(
            f"Processed INVALID order: {order.get('order_id')} "
            f"errors={error_event['error_reason']}"
        )


def main():
    consumer.subscribe([SOURCE_TOPIC])

    logging.info("Kafka consumer started.")
    logging.info("Listening to topic: %s", SOURCE_TOPIC)

    try:
        while True:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue

            if msg.error():
                raise KafkaException(msg.error())

            process_message(msg.value())

            consumer.commit(asynchronous=False)

            producer.flush()

    except KeyboardInterrupt:
        logging.info("Consumer stopped by user.")

    finally:
        consumer.close()
        producer.flush()
        logging.info("Consumer closed.")


if __name__ == "__main__":
    main()
