import httpClient from "../../../shared/api/axiosInstance";
import { SERVER_URL } from "../../../shared/const/serverUrl";

interface CreateTaskResponse {
  status: string;
  task_id?: string;
}

export async function createTaskApi(
  title: string,
  creatorName: string
): Promise<CreateTaskResponse> {
  const response = await httpClient.post<CreateTaskResponse>(
    `${SERVER_URL}/create_task`,
    {
      title,
      creator_username: creatorName,
    }
  );
  return response.data;
}