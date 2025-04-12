import threading
import time
import pika
from pika.exceptions import StreamLostError


class RabbitMQBase:
    def __init__(self, rabbitmq_host, username, password):
        self.username = username
        self.password = password
        self.rabbitmq_host = rabbitmq_host
        self._connect()
        threading.Thread(target=self._send_heartbeat, daemon=True).start()

    def _connect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.rabbitmq_host,
                credentials=pika.PlainCredentials(self.username, self.password),
                heartbeat=600
            )
        )
        self.channel = self.connection.channel()

    def _reconnect(self):
        self._connect()

    def _send_heartbeat(self):
        while True:
            try:
                self.connection.process_data_events()
                time.sleep(10)
            except StreamLostError as e:
                self._reconnect()
            except Exception as e:
                self._reconnect()

    def close(self):
        try:
            self.channel.close()
        finally:
            self.connection.close()

