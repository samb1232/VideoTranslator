import { TaskData } from "../../../entities/task";

export interface ApiResponse {
    status: string;
    tasks: TaskData[];
  }