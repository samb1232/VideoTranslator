export interface User {
    id: string;
    username: string;
}

export interface TaskDescription {
    id: string;
    last_used: string;
    title: string;
  }
  
export interface ApiResponse {
    status: string;
    tasks: TaskDescription[];
  }