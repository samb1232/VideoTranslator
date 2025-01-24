import { TaskData } from "../../../entities/task/model/taskData";

export interface ApiResponse {
    status: string;
    tasks: TaskData[];
  }