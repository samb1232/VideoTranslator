import { useEffect, useState } from "react";
import { ApiResponse, TaskDescription, User } from "../utils/types";
import { Link, useNavigate } from "react-router-dom";
import httpClient from "../utils/httpClient";
import TaskItem from "./TaskItem";
import CreateTaskWindow from "./CreateTaskWindow";

import styles from "./styles/home.module.css";
import { SERVER_URL } from "../utils/serverInfo";

function HomePage() {
  const [user, setUser] = useState<User | null>(null);
  const [tasks, setTasks] = useState<TaskDescription[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    getUserInfo();
    fetchTasks();
  }, []);

  const logoutUser = async () => {
    await httpClient.post(`${SERVER_URL}/api/logout`);
    navigate("/login", { replace: true });
  };

  const getUserInfo = async () => {
    try {
      const resp = await httpClient.get(`${SERVER_URL}/api/@me`);
      if (resp.data) {
        setUser(resp.data);
      } else {
        navigate("/login", { replace: true });
      }
    } catch (error) {
      navigate("/login", { replace: true });
    }
  };

  const fetchTasks = async () => {
    try {
      const response = await httpClient.get<ApiResponse>(
        `${SERVER_URL}/api/get_all_tasks`
      );
      if (response.data.status === "success") {
        setTasks(response.data.tasks);
      } else {
        setError("Failed to fetch tasks");
      }
    } catch (err) {
      setError("Error fetching tasks");
    } finally {
      setLoading(false);
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
      <h1>ExtFo Video Translator</h1>
      <ul className={styles.task_list}>
        <li className={styles.create_task_button} onClick={openModal}>
          +
          <br />
          Create new task
        </li>
        {loading ? (
          <div className={styles.loading_tasks_div}>Loading...</div>
        ) : error ? (
          <div>{error}</div>
        ) : (
          tasks.map((task) => (
            <Link
              key={task.id}
              className={styles.link_taskItem}
              to={"/task/" + task.id}
            >
              <TaskItem key={task.id} task={task} />
            </Link>
          ))
        )}
      </ul>
      {isModalOpen && (
        <CreateTaskWindow closeWindowFunc={() => setIsModalOpen(false)} />
      )}
    </div>
  );
}

export default HomePage;
