import enum

class TaskStatus(enum.Enum):
    idle = "Idle"
    queued = "Queued"
    processing =  "Processing"
    error = "Error"
