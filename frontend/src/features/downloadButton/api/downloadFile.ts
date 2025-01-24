import { SERVER_URL } from "../../../shared/const/serverUrl";
import httpClient from "../../../shared/api/axiosInstance";

export async function downloadFile(filepath: string): Promise<Blob> {
    const response = await httpClient.get(
        `${SERVER_URL}/download/${filepath}`,
        {
            responseType: "blob",
        }
    );
    return new Blob([response.data]);
}