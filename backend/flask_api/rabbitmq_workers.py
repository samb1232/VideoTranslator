import os
import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from logging_conf import setup_logging
from database.db_helper import DbHelper
from utils.task_status_enum import TaskStatus
from utils.queue_tasks import RabbitMqOperationTypes, ResultsQueueItem, SubsGenQueueItem, SubsGenResultsItem, VoiceGenQueueItem, VoiceGenResultsItem
from config import ConfigWeb

logger = setup_logging()

db_operations: DbHelper = DbHelper()
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', 5672))


class RabbitMQProducer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT
            )
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=ConfigWeb.RABBITMQ_SUBS_GEN_QUEUE, durable=True)
        self.channel.queue_declare(queue=ConfigWeb.RABBITMQ_VOICE_GEN_QUEUE, durable=True)
        logger.info("RabbitMQ producer channel connected")

    def add_task_to_subs_gen_queue(self, task: SubsGenQueueItem):
        db_operations.set_task_subs_generation_status(task_id=task.task_id, status=TaskStatus.QUEUED)
        self.channel.basic_publish(
            exchange='',
            routing_key=ConfigWeb.RABBITMQ_SUBS_GEN_QUEUE,
            body=task.to_json(),
            properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
            )
        )
        logger.debug(f"Task {task.task_id} added to subs generation queue")

    def add_task_to_voice_gen_queue(self, task: VoiceGenQueueItem):
        db_operations.set_task_voice_generation_status(task_id=task.task_id, status=TaskStatus.QUEUED)
        self.channel.basic_publish(
            exchange='',
            routing_key=ConfigWeb.RABBITMQ_VOICE_GEN_QUEUE,
            body=task.to_json(),
            properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
            )
        )
        logger.debug(f"Task {task.task_id} added to voice generation queue")

    def close(self):
        try:
            self.channel.close()
        except Exception as e:
            logger.error(f"Error closing producer channel: {e}")
        finally:
            self.connection.close()
            logger.info("RabbitMQ producer connection closed")
               

class RabbitMQConsumer:
    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT
            )
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=ConfigWeb.RABBITMQ_RESULTS_QUEUE, durable=True)
        logger.info("RabbitMQ consumer channel connected")

    def callback(self, ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: str | bytes):
        #TODO: сделать проверку body json на корректность
        res_item = ResultsQueueItem.from_json(body)

        new_status = res_item.op_status
        if new_status != TaskStatus.IDLE:
            if res_item.op_type == RabbitMqOperationTypes.SUBS_GEN:
                db_operations.set_task_subs_generation_status(
                    task_id=res_item.task_id,
                status=new_status
                    )
            else:
                db_operations.set_task_voice_generation_status(
                    task_id=res_item.task_id,
                    status=new_status
                    )
            logger.debug(f"Task {res_item.task_id} status updated to {new_status.name} for operation {res_item.op_type.name}")
        else:
            results = res_item.results
            if res_item.op_type == RabbitMqOperationTypes.SUBS_GEN:
                assert type(results) == SubsGenResultsItem
                db_operations.update_task_after_subs_generated(
                    task_id=res_item.task_id,
                    src_audio_path=results.src_audio_path,
                    srt_orig_subs_path=results.srt_orig_subs_path,
                    srt_translated_subs_path=results.srt_translated_subs_path,
                    json_translated_subs_path=results.json_translated_subs_path
                    )
            else:
                assert type(results) == VoiceGenResultsItem
                db_operations.update_task_after_voice_generated(
                    task_id=res_item.task_id,
                    translated_audio_path=results.translated_audio_path,
                    translated_video_path=results.translated_video_path
                    )
            logger.debug(f"Task {res_item.task_id} status updated to {new_status.name} for operation {res_item.op_type.name}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def watch_results_queue(self):
        self.channel.basic_consume(queue=ConfigWeb.RABBITMQ_RESULTS_QUEUE, on_message_callback=self.callback)

        logger.info('Starting to listen results queue')
        self.channel.start_consuming()

    @staticmethod
    def check_body_json_format(body_json: dict) -> bool:
        # TODO: изменить входной тип на строку json. Актуализировать проверку.
        if not isinstance(body_json.get("task_id"), str):
            return False
        if body_json.get("op_type") not in ["subs_gen", "voice_gen"]:
            return False
        if body_json.get("op_status") not in ["processing", "done", "error"]:
            return False

        # Проверка поля results в зависимости от op_type
        op_type = body_json["op_type"]
        op_status = body_json["op_status"]

        if op_status == "done":
            results = body_json.get("results", {})
            if op_type == "subs_gen":
                required_fields = [
                    "src_vid_path",
                    "src_audio_path",
                    "srt_orig_subs_path",
                    "srt_translated_subs_path",
                    "json_translated_subs_path"
                ]
            elif op_type == "voice_gen":
                required_fields = [
                    "translated_audio_path",
                    "translated_video_path"
                ]

            for field in required_fields:
                if field not in results:
                    return False

        return True

    def close(self):
        try:
            self.channel.close()
        except Exception as e:
            logger.error(f"Error closing consumer channel: {e}")
        finally:
            self.connection.close()
            logger.info("RabbitMQ consumer connection closed")