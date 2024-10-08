import { useEffect, useState } from "react";
import { ApiResponse, TaskDescription, User } from "../utils/types";
import { Link, useNavigate } from "react-router-dom";
import httpClient from "../utils/httpClient";
import TaskItem from "./TaskItem";
import CreateTaskWindow from "./CreateTaskWindow";

import styles from "./styles/home.module.css";

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
    await httpClient.post("//localhost:5000/logout");
    navigate("/login", { replace: true });
  };

  const getUserInfo = async () => {
    try {
      const resp = await httpClient.get("//localhost:5000/@me");
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
        "http://localhost:5000/get_all_tasks"
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

  const handleDeleteTask = async (id: string) => {
    try {
      const response = await httpClient.delete(
        "//localhost:5000/delete_task/" + id
      );
      if (response.data.status === "success") {
        // refresh tasks list
        // fetchTasks();
        navigate("/");
      }
    } catch (error) {
      console.error("Error deleting task:", error);
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
              <TaskItem key={task.id} task={task} onDelete={handleDeleteTask} />
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
