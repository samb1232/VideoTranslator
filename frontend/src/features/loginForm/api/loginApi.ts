import httpClient from '../../../shared/api/axiosInstance';
import { SERVER_URL } from '../../../shared/const/serverUrl';

export async function checkAuth() {
  return await httpClient.get(`${SERVER_URL}/@me`);
}

export async function loginUser(username: string, password: string) {
  return await httpClient.post(`${SERVER_URL}/login_user`, {
    username,
    password,
  });
}
