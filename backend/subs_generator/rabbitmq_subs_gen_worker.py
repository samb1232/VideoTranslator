import os
import pika
from logging_conf import setup_logging
from shared_utils.rabbitmq_base import RabbitMQBase
from shared_utils.task_status_enum import TaskStatus
from subs_translator import SubsTranslator, Translators
from subs_generator import SubsGenerator
from shared_utils.file_utils import get_task_folder
from shared_utils.queue_tasks import RabbitMqOperationTypes, ResultsQueueItem, SubsGenQueueItem, SubsGenResultsItem
import config
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

logger = setup_logging()

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')


class RabbitMQSubsGenWorker(RabbitMQBase):
    def __init__(self):
        super().__init__(rabbitmq_host=RABBITMQ_HOST, username=RABBITMQ_USER, password=RABBITMQ_PASSWORD)
        self.channel.queue_declare(queue=config.RABBITMQ_RESULTS_QUEUE, durable=True)
        self.channel.queue_declare(queue=config.RABBITMQ_SUBS_GEN_QUEUE, durable=True)
        logger.info("RabbitMQ subs gen worker connected")
        

    def watch_subs_gen_queue(self):
        while True:
            try:
                self.channel.basic_consume(queue=config.RABBITMQ_SUBS_GEN_QUEUE, on_message_callback=self._callback)
                logger.info('Starting to subs_gen queue')
                self.channel.start_consuming()
            except Exception as e:
                logger.error(f"Error while consuming results queue: {e}")
                self._reconnect()

    def _reconnect(self):
        super()._reconnect()
        self.watch_subs_gen_queue()

    def _publish_message(self, queue: str, body_json: str):
        self.channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=body_json,
            properties=pika.BasicProperties(delivery_mode=2,)  # make message persistent
        )
    
    def _callback(self, ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: str | bytes):
        task_item = SubsGenQueueItem.from_json(body)
        logger.debug(f"Received task: {task_item.task_id}")
        
        return_message = ResultsQueueItem(
            task_id=task_item.task_id,
            op_type=RabbitMqOperationTypes.SUBS_GEN,
            op_status=TaskStatus.PROCESSING
        )
        
        self._publish_message(queue=config.RABBITMQ_RESULTS_QUEUE, body_json=return_message.to_json())
        
        try:
            result = self._generate_subs(task_item)
            logger.info(f"Task {task_item.task_id} done")
            return_message.op_status = TaskStatus.IDLE
            return_message.results = result
        except Exception as e:
            logger.exception(e)
            return_message.op_status = TaskStatus.ERROR
        
        logger.debug(f"Sending task {task_item.task_id} to res queue with status {return_message.op_status.name}")    
        
        self._publish_message(queue=config.RABBITMQ_RESULTS_QUEUE, body_json=return_message.to_json())
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    @staticmethod
    def _generate_subs(task: SubsGenQueueItem) -> SubsGenResultsItem:
        file_exists = os.path.exists(task.vid_filepath)
        if not file_exists:
            message = f"File {task.vid_filepath} does not exist"
            logger.error(message)
            raise FileNotFoundError(message)

        task_folder = get_task_folder(task.task_id)
        
        subs_generator = SubsGenerator(src_lang=task.lang_from)
        subs_generator.transcript(
            video_file_path=task.vid_filepath,
            output_dir=task_folder
            )
        json_filepath = subs_generator.get_json_out_filepath()
        srt_filepath = subs_generator.get_srt_out_filepath()
        audio_filepath = subs_generator.get_audio_out_filepath()

        subs_translator = SubsTranslator(
            translator=Translators.yandex,
            source_lang=task.lang_from,
            target_lang=task.lang_to
            )

        srt_tranlsated_filepath = os.path.join(task_folder, f"{task.task_id}_translated.srt")
        json_tranlsated_filepath = os.path.join(task_folder, f"{task.task_id}_translated.json")

        subs_translator.translate_srt_file(srt_filepath, srt_tranlsated_filepath)
        subs_translator.translate_json_file(json_filepath, json_tranlsated_filepath)
        
        result = SubsGenResultsItem(
            src_audio_path = audio_filepath,
            srt_orig_subs_path = srt_filepath,
            srt_translated_subs_path = srt_tranlsated_filepath,
            json_translated_subs_path = json_tranlsated_filepath
        )
        
        return result
    

if __name__ == "__main__":
    worker = RabbitMQSubsGenWorker()
    worker.watch_subs_gen_queue()
