import { TaskData } from "./taskData";

export interface ApiResponse {
    status: string;
    tasks: TaskData[];
  }