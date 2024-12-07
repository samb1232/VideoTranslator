import os
import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties
from pika.exceptions import StreamLostError
from shared_utils.rabbitmq_base import RabbitMQBase
from logging_conf import setup_logging
from database.db_helper import DbHelper
from shared_utils.task_status_enum import TaskStatus
from shared_utils.queue_tasks import RabbitMqOperationTypes, ResultsQueueItem, SubsGenQueueItem, SubsGenResultsItem, VoiceGenQueueItem, VoiceGenResultsItem
from config import ConfigWeb

logger = setup_logging()

db_operations: DbHelper = DbHelper()
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')

class RabbitMQProducer(RabbitMQBase):
    def __init__(self):
        super().__init__(rabbitmq_host=RABBITMQ_HOST)
        self.channel.queue_declare(queue=ConfigWeb.RABBITMQ_SUBS_GEN_QUEUE, durable=True)
        self.channel.queue_declare(queue=ConfigWeb.RABBITMQ_VOICE_GEN_QUEUE, durable=True)

    def _publish_message(self, queue: str, body_json: str):
        self.channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=body_json,
            properties=pika.BasicProperties(delivery_mode=2,)  # make message persistent
        )

    def add_task_to_subs_gen_queue(self, task: SubsGenQueueItem):
        try:
            queue = ConfigWeb.RABBITMQ_SUBS_GEN_QUEUE
            self._publish_message(queue=queue, body_json=task.to_json())
            db_operations.set_task_subs_generation_status(task_id=task.task_id, status=TaskStatus.QUEUED)
            logger.debug(f"Task {task.task_id} added to {queue} queue")
        except StreamLostError as e:
            logger.error(f"Error adding task to {queue} queue: {e}")
            self._reconnect()
        except Exception as e:
            logger.error(f"Unknown exception: {e}")
            self._reconnect()

    def add_task_to_voice_gen_queue(self, task: VoiceGenQueueItem):
        try:
            queue = ConfigWeb.RABBITMQ_VOICE_GEN_QUEUE
            self._publish_message(queue=queue, body_json=task.to_json())
            db_operations.set_task_voice_generation_status(task_id=task.task_id, status=TaskStatus.QUEUED)
            logger.debug(f"Task {task.task_id} added to {queue} queue")
        except StreamLostError as e:
            logger.error(f"Error adding task to {queue} queue: {e}")
            self._reconnect()
        except Exception as e:
            logger.error(f"Unknown exception: {e}")
            self._reconnect()
        
        
class RabbitMQConsumer(RabbitMQBase):
    def __init__(self):
        super().__init__(rabbitmq_host=RABBITMQ_HOST)
        self.channel.queue_declare(queue=ConfigWeb.RABBITMQ_RESULTS_QUEUE, durable=True)
        logger.info("RabbitMQ results channel connected")
        
    def watch_results_queue(self):
            while True:
                try:
                    self.channel.basic_consume(queue=ConfigWeb.RABBITMQ_RESULTS_QUEUE, on_message_callback=self._callback)
                    logger.info('Starting to listen results queue')
                    self.channel.start_consuming()
                except Exception as e:
                    logger.error(f"Error while consuming results queue: {e}")
                    self._reconnect()
                    
    def _reconnect(self):
        super()._reconnect()
        self.watch_results_queue()

    def _callback(self, ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: str | bytes):
        res_item = ResultsQueueItem.from_json(body)
        new_status = res_item.op_status
        if new_status != TaskStatus.IDLE:
            self._update_task_status(res_item, new_status)
        else:
            self._update_task_results(res_item)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def _update_task_status(self, res_item: ResultsQueueItem, new_status: TaskStatus):
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

    def _update_task_results(self, res_item: ResultsQueueItem):
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
        logger.debug(f"Task {res_item.task_id} status updated to {res_item.op_status.name} for operation {res_item.op_type.name}")

    

    @staticmethod
    def check_body_json_format(body_json: dict) -> bool:
        if not isinstance(body_json.get("task_id"), str):
            return False
        if body_json.get("op_type") not in ["subs_gen", "voice_gen"]:
            return False
        if body_json.get("op_status") not in ["processing", "done", "error"]:
            return False

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
