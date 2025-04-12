import os
import pika
from config_rabbitmq import ConfigRabbitMQ
from shared_utils.rabbitmq_base import RabbitMQBase
from shared_utils.task_status_enum import TaskStatus
from shared_utils.file_utils import get_task_folder
from shared_utils.queue_tasks import RabbitMqOperationTypes, ResultsQueueItem, VoiceGenQueueItem, VoiceGenResultsItem
from logging_conf import setup_logging
from voice_generator import VoiceGenerator
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties


logger = setup_logging()

RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')


class RabbitMQVoiceGenWorker(RabbitMQBase):
    def __init__(self):
        self.voice_generator = VoiceGenerator()
        super().__init__(rabbitmq_host=RABBITMQ_HOST, username=RABBITMQ_USER, password=RABBITMQ_PASSWORD)
        self.channel.queue_declare(queue=ConfigRabbitMQ.RABBITMQ_RESULTS_QUEUE, durable=True)
        self.channel.queue_declare(queue=ConfigRabbitMQ.RABBITMQ_VOICE_GEN_QUEUE, durable=True)
        logger.info("RabbitMQ voice gen worker connected")
        
    def watch_voice_gen_queue(self):
        while True:
            try:
                self.channel.basic_consume(queue=ConfigRabbitMQ.RABBITMQ_VOICE_GEN_QUEUE, on_message_callback=self._callback)
                logger.info('Starting to voice_gen queue')
                self.channel.start_consuming()
            except Exception as e:
                logger.error(f"Error while consuming results queue: {e}")
                self._reconnect()

    def _reconnect(self):
        super()._reconnect()
        self.watch_voice_gen_queue()

    def _publish_message(self, queue: str, body_json: str):
        self.channel.basic_publish(
            exchange='',
            routing_key=queue,
            body=body_json,
            properties=pika.BasicProperties(delivery_mode=2,)  # make message persistent
        )
    
    def _callback(self, ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: str | bytes):
        task_item = VoiceGenQueueItem.from_json(body)
        logger.debug(f"Received task: {task_item.task_id}")
        
        return_message = ResultsQueueItem(
            task_id=task_item.task_id,
            op_type=RabbitMqOperationTypes.VOICE_GEN,
            op_status=TaskStatus.PROCESSING
        )
        
        logger.debug(f"Sending task {task_item.task_id} to res queue with status {return_message.op_status.name}")   
        self._publish_message(queue=ConfigRabbitMQ.RABBITMQ_RESULTS_QUEUE, body_json=return_message.to_json())
        logger.debug(f"Task sent to queue")   
        
        try:
            result = self._generate_voice(task_item)
            logger.info(f"Task {task_item.task_id} done")
            return_message.op_status = TaskStatus.IDLE
            return_message.results = result
        except Exception as e:
            logger.exception(e)
            return_message.op_status = TaskStatus.ERROR
        
        logger.debug(f"Sending task {task_item.task_id} to res queue with status {return_message.op_status.name}")    
        self._publish_message(queue=ConfigRabbitMQ.RABBITMQ_RESULTS_QUEUE, body_json=return_message.to_json())
        logger.debug(f"Task sent to queue")   
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def _generate_voice(self, task: VoiceGenQueueItem) -> VoiceGenResultsItem:
        files_exists = os.path.exists(task.json_subs_path) & os.path.exists(task.src_audio_path) & os.path.exists(task.src_video_path)
        if not files_exists:
            message = f"Some files in task {task.task_id} does not exist"
            logger.error(message)
            raise FileNotFoundError(message)

        task_folder = get_task_folder(task.task_id)
        
        final_audio_filepath = os.path.join(task_folder, f"{task.task_id}_audio_{task.lang_to}.wav")
        final_video_filepath = os.path.join(task_folder, f"{task.task_id}_vid_{task.lang_to}.mp4")

        self.voice_generator.generate_audio(
            orig_wav_filepath=task.src_audio_path,
            language=task.lang_to,
            json_subs_filepath=task.json_subs_path,
            out_wav_filepath=final_audio_filepath,
            )
        self.voice_generator.replace_audio_in_video(
            in_audio_path=final_audio_filepath,
            in_video_path=task.src_video_path,
            out_video_path=final_video_filepath
            )
        
        result = VoiceGenResultsItem(
            translated_audio_path=final_audio_filepath,
            translated_video_path=final_video_filepath
        )
        
        return result


if __name__ == "__main__":
    worker = RabbitMQVoiceGenWorker()
    worker.watch_voice_gen_queue()
