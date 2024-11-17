import os
import pika
from logging_conf import setup_logging
from utils.task_status_enum import TaskStatus
from voice_generator import VoiceGenerator
from utils.file_utils import get_task_folder
from utils.queue_tasks import RabbitMqOperationTypes, ResultsQueueItem, VoiceGenQueueItem, VoiceGenResultsItem
import config
from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

logger = setup_logging()


rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
rabbitmq_port = int(os.getenv('RABBITMQ_PORT', 5672))


def callback(ch: BlockingChannel, method: Basic.Deliver, properties: BasicProperties, body: str | bytes):
    #TODO: сделать проверку body json на корректность
    task_item = VoiceGenQueueItem.from_json(body)
    logger.debug(f"Received task: {task_item.task_id}")
    
    return_message = ResultsQueueItem(
        task_id=task_item.task_id,
        op_type=RabbitMqOperationTypes.VOICE_GEN,
        op_status=TaskStatus.PROCESSING
    )
    
    logger.debug(f"Sending task {task_item.task_id} to res queue with status {return_message.op_status.name}") 
    ch.basic_publish(
        exchange='', 
        routing_key=config.RABBITMQ_RESULTS_QUEUE, 
        body=return_message.to_json(),
        properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
        )
    
    try:
        result = generate_voice(task_item)
        logger.info(f"Task {task_item.task_id} done")
        return_message.op_status = TaskStatus.IDLE
        return_message.results = result
    except Exception as e:
        error_msg = str(e)
        return_message.op_status = TaskStatus.ERROR
       
    logger.debug(f"Sending task {task_item.task_id} to res queue with status {return_message.op_status.name}")    
    ch.basic_publish(
        exchange='', 
        routing_key=config.RABBITMQ_RESULTS_QUEUE, 
        body=return_message.to_json(),
        properties=pika.BasicProperties(delivery_mode=2)  # make message persistent
        )
    ch.basic_ack(delivery_tag=method.delivery_tag)


def generate_voice(task: VoiceGenQueueItem):
    files_exists = os.path.exists(task.json_subs_path) & os.path.exists(task.src_audio_path) & os.path.exists(task.src_video_path)
    if not files_exists:
        message = f"Some files in task {task.task_id} does not exist"
        logger.error(message)
        raise FileNotFoundError(message)

    task_folder = get_task_folder(task.task_id)
    
    final_audio_filepath = os.path.join(task_folder, f"{task.task_id}_audio_{task.lang_to}.wav")
    final_video_filepath = os.path.join(task_folder, f"{task.task_id}_vid_{task.lang_to}.mp4")

    voice_generator = VoiceGenerator(task.lang_to)
    voice_generator.generate_audio(
        orig_wav_filepath=task.src_audio_path,
        json_subs_filepath=task.json_subs_path,
        out_wav_filepath=final_audio_filepath
        )
    voice_generator.replace_audio_in_video(
        in_audio_path=final_audio_filepath,
        in_video_path=task.src_video_path,
        out_video_path=final_video_filepath
        )
    
    result = VoiceGenResultsItem(
        translated_audio_path=final_audio_filepath,
        translated_video_path=final_video_filepath
    )
    
    return result

    
def main():
    connection = pika.BlockingConnection(
            pika.ConnectionParameters(
            host=rabbitmq_host,
            port=rabbitmq_port
            )
        )

    channel = connection.channel()
    channel.queue_declare(queue=config.RABBITMQ_VOICE_GEN_QUEUE, durable=True)
    channel.queue_declare(queue=config.RABBITMQ_RESULTS_QUEUE, durable=True)
    logger.info("RabbitMQ channel connected successfully")

    channel.basic_consume(queue=config.RABBITMQ_VOICE_GEN_QUEUE, on_message_callback=callback)

    logger.info('Starting listening voice_gen queue')
    channel.start_consuming()


if __name__ == "__main__":
    main()
