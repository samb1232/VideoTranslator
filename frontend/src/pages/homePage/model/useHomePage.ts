import { useState } from "react";
import { useNavigate } from "react-router-dom";
import httpClient from "../../../shared/api/axiosInstance";
import { SERVER_URL } from "../../../shared/const/serverUrl";
import { User } from "../types/user";

export function useHomePage() {
  const [user, setUser] = useState<User | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const navigate = useNavigate();

  const fetchUserInfo = async () => {
    try {
      const resp = await httpClient.get(`${SERVER_URL}/@me`);
      if (resp.data) {
        setUser(resp.data);
      } else {
        navigate("/login", { replace: true });
      }
    } catch (error) {
      navigate("/login", { replace: true });
    }
  };

  const logoutUser = async () => {
    await httpClient.post(`${SERVER_URL}/logout`);
    navigate("/login", { replace: true });
  };

  const openModal = () => {
    setIsModalOpen(true);
  };

  return {
    user,
    isModalOpen,
    setIsModalOpen,
    logoutUser,
    openModal,
    fetchUserInfo,
  };
}