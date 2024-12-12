import pika, sys, os, time
from pymongo import MongoClient
import gridfs
from convert import to_mp3

def main():
    client = MongoClient("mongodb-service", 27017)
    db_videos = client.videos
    db_mp3s = client.mp3s
    # gridfs
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    # rabbitmq connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq.default.svc.cluster.local", port=5672, heartbeat=600,))
    channel = connection.channel()
    channel.basic_qos(prefetch_count=5)
    channel.queue_declare(
        queue=os.environ.get("VIDEO_QUEUE"),
        durable=True,
        auto_delete=False,
        exclusive=False
    )

    def callback(ch, method, properties, body):
        try:
            print(f"Received message: {body}")
            err = to_mp3.start(body, fs_videos, fs_mp3s, ch)
            if err:
                print(f"Failed to process message: {err}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            else:
                ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            print(f"Callback processing error: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    print("Waiting for messages. To exit press CTRL+C")
    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
    )

    channel.start_consuming()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
