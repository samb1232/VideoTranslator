import httpClient from "./httpClient";

export default async function uploadFileToServer(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await httpClient.post('http://localhost:5000/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
}