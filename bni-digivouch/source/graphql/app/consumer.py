from kafka import KafkaConsumer
import json

if __name__ == "__main__":
    consumer = KafkaConsumer(
        "ayopop",
        bootstrap_servers='localhost:9092',
        auto_offset_reset='latest',
        group_id="consumer-group-a")
    print("starting the consumer")
    for msg in consumer:
        print("payment ayopop = {}".format(json.loads(msg.value)))
