import httpClient from '../../../shared/api/axiosInstance';
import { SERVER_URL } from '../../../shared/const/serverUrl';
import { LoginResponse } from '../types/loginResponse';

export async function checkAuth() {
  return await httpClient.get(`${SERVER_URL}/@me`);
}

export async function loginUser(username: string, password: string): Promise<LoginResponse> {
  return await httpClient.post(`${SERVER_URL}/login_user`, {
    username,
    password,
  });
}
