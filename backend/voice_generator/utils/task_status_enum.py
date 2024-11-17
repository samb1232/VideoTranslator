from enum import Enum

class TaskStatus(Enum):
    IDLE = "Idle"
    QUEUED = "Queued"
    PROCESSING =  "Processing"
    ERROR = "Error"
