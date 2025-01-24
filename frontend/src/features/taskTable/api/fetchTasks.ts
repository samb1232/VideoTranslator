import httpClient from "../../../shared/api/axiosInstance";
import { SERVER_URL } from "../../../shared/const/serverUrl";
import { ApiResponse } from "../types/apiResponse";

export async function fetchTasks(): Promise<ApiResponse> {
  const response = await httpClient.get<ApiResponse>(
    `${SERVER_URL}/get_all_tasks`
  );
  return response.data;
}