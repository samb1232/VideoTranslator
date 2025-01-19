import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import styles from "./styles/home.module.css";
import { User } from "../../../entities/user/user";
import { SERVER_URL } from "../../../shared/const/serverUrl";
import httpClient from "../../../shared/api/axiosInstance";
import { TaskTable } from "../../../entities/TaskTable";
import { CreateNewTaskForm } from "../../../features/createNewTaskForm";

export function HomePage() {
  const [user, setUser] = useState<User | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    getUserInfo();
  }, []);

  const logoutUser = async () => {
    await httpClient.post(`${SERVER_URL}/logout`);
    navigate("/login", { replace: true });
  };

  const getUserInfo = async () => {
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

  const openModal = () => {
    setIsModalOpen(true);
  };

  return (
    <div className={styles.body}>
      <div className={styles.top_right}>
        <div>Hello, {user?.username}</div>
        <button className={styles.logout_button} onClick={logoutUser}>
          Logout
        </button>
      </div>
      <h1 className={styles.extfo_h1}>ExtFo Video Translator</h1>
      <ul className={styles.task_list}>
        <li className={styles.create_task_button} onClick={openModal}>
          +
          <br />
          Create new task
        </li>
        <TaskTable />
      </ul>
      {isModalOpen && (
        <CreateNewTaskForm
          closeWindowFunc={() => setIsModalOpen(false)}
          creatorName={user?.username}
        />
      )}
    </div>
  );
}

export default HomePage;
