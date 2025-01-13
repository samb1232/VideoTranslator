

export interface ApiResponse {
  status: string;
  tasks: TaskData[];
}



export enum TaskStatus {
  idle = "Idle",
  queued = "Queued",
  processing =  "Processing",
  error = "Error",
}
