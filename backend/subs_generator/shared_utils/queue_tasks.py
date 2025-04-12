from enum import Enum, auto
import json

from shared_utils.task_status_enum import TaskStatus

    
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

    def __eq__(self, other):
        if isinstance(other, SubsGenQueueItem):
            return (self.task_id == other.task_id and
                    self.vid_filepath == other.vid_filepath and
                    self.lang_from == other.lang_from and
                    self.lang_to == other.lang_to
                    )
        return False
    

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

    def __eq__(self, other):
        if isinstance(other, SubsGenResultsItem):
            return (self.src_audio_path == other.src_audio_path and
                    self.srt_orig_subs_path == other.srt_orig_subs_path and
                    self.srt_translated_subs_path == other.srt_translated_subs_path and
                    self.json_translated_subs_path == other.json_translated_subs_path
                    )
        return False

    
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
    
    def __eq__(self, other):
        if isinstance(other, VoiceGenQueueItem):
            return (self.task_id == other.task_id and
                    self.src_audio_path == other.src_audio_path and
                    self.src_video_path == other.src_video_path and
                    self.json_subs_path == other.json_subs_path and
                    self.lang_to == other.lang_to)
        return False
 
 
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
    
    def __eq__(self, other):
        if isinstance(other, VoiceGenResultsItem):
            return (self.translated_audio_path == other.translated_audio_path and
                    self.translated_video_path == other.translated_video_path
                    )
        return False
    

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
        
    def __eq__(self, other):
        if isinstance(other, ResultsQueueItem):
            return (self.task_id == other.task_id and
                    self.op_type == other.op_type and
                    self.op_type == other.op_type and
                    self.op_status == other.op_status and
                    self.results == other.results
                    )
        return False
