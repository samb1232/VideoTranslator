from enum import Enum, auto
import json

from utils.task_status_enum import TaskStatus

    
class RabbitMqOperationTypes(Enum):
    SUBS_GEN = auto()
    VOICE_GEN = auto()


class SubsGenQueueItem:
    def __init__(self, task_id: str, vid_filepath: str, lang_from: str, lang_to: str):
        self.task_id = task_id
        self.vid_filepath = vid_filepath
        self.lang_from = lang_from
        self.lang_to = lang_to

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @staticmethod
    def from_json(json_str: str):
        json_dict = json.loads(json_str)
        return SubsGenQueueItem(**json_dict)


class SubsGenResultsItem:
    def __init__(self, src_audio_path: str, srt_orig_subs_path: str, srt_translated_subs_path: str, json_translated_subs_path: str):
        self.src_audio_path = src_audio_path
        self.srt_orig_subs_path = srt_orig_subs_path
        self.srt_translated_subs_path = srt_translated_subs_path
        self.json_translated_subs_path = json_translated_subs_path 
    
    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    @staticmethod
    def from_json(json_str: str):
        json_dict = json.loads(json_str)
        return SubsGenResultsItem(**json_dict)


class VoiceGenQueueItem:
    def __init__(self, task_id: str, src_audio_path: str, src_video_path: str, json_subs_path: str, lang_to: str):
        self.task_id = task_id
        self.src_audio_path = src_audio_path
        self.src_video_path = src_video_path
        self.json_subs_path = json_subs_path
        self.lang_to = lang_to

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    @staticmethod
    def from_json(json_str: str):
        json_dict = json.loads(json_str)
        return VoiceGenQueueItem(**json_dict)
 
 
class VoiceGenResultsItem:
    def __init__(self, translated_audio_path: str, translated_video_path: str):
        self.translated_audio_path = translated_audio_path
        self.translated_video_path = translated_video_path
    
    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    @staticmethod
    def from_json(json_str: str):
        json_dict = json.loads(json_str)
        return VoiceGenResultsItem(**json_dict)
    

class ResultsQueueItem: 
    def __init__(
        self, 
        task_id: str, 
        op_type: RabbitMqOperationTypes, 
        op_status: TaskStatus, 
        results: SubsGenResultsItem | VoiceGenResultsItem | None = None
        ):
        self.task_id = task_id
        self.op_type = op_type
        self.op_status = op_status
        self.results = results
        
    def to_json(self) -> str:
        json_dict = {
            "task_id": self.task_id,
            "op_type": self.op_type.name,
            "op_status": self.op_status.name,
        }
        if self.results is not None:
            json_dict["results"] = self.results.to_json()
        return json.dumps(json_dict, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    @staticmethod
    def from_json(json_str: str):
        json_dict = json.loads(json_str)
        
        task_id = json_dict["task_id"]
        op_type = getattr(RabbitMqOperationTypes, json_dict["op_type"])
        op_status = getattr(TaskStatus, json_dict["op_status"])
        
        if "results" in json_dict:
            if op_type == RabbitMqOperationTypes.SUBS_GEN:
                results = SubsGenResultsItem.from_json(json_dict["results"])
            else:
                results = VoiceGenResultsItem.from_json(json_dict["results"])
        else:
            results = None
        
        return ResultsQueueItem(task_id, op_type, op_status, results)
        