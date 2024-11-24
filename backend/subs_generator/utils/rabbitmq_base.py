import threading
import time
from logging_conf import setup_logging
import pika
from pika.exceptions import StreamLostError


logger = setup_logging()

class RabbitMQBase:
    def __init__(self, rabbitmq_host):
        self.rabbitmq_host = rabbitmq_host
        self._connect()
        threading.Thread(target=self._send_heartbeat, daemon=True).start()

    def _connect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.rabbitmq_host,
                heartbeat=600
            )
        )
        self.channel = self.connection.channel()
        logger.info("RabbitMQ channel connected")

    def _reconnect(self):
        logger.info("Reconnecting to RabbitMQ...")
        self._connect()

    def _send_heartbeat(self):
        while True:
            try:
                self.connection.process_data_events()
                time.sleep(10)
            except StreamLostError as e:
                logger.error(f"Error in heartbeat: {e}")
                self._reconnect()
            except Exception as e:
                logger.error(f"Unknown exception: {e}")
                self._reconnect()

    def close(self):
        try:
            self.channel.close()
        except Exception as e:
            logger.error(f"Error closing channel: {e}")
        finally:
            self.connection.close()
            logger.info("RabbitMQ connection closed")
