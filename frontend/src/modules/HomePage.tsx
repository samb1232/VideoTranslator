import { useEffect, useState } from "react";
import { ApiResponse, TaskData, TaskStatus, User } from "../utils/types";
import { Link, useNavigate } from "react-router-dom";
import httpClient from "../utils/httpClient";
import CreateTaskWindow from "./CreateTaskWindow";

import styles from "./styles/home.module.css";
import { SERVER_URL } from "../utils/serverInfo";
import { formatDate } from "../utils/dateFormatter";

function HomePage() {
  const [user, setUser] = useState<User | null>(null);
  const [tasks, setTasks] = useState<TaskData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    getUserInfo();
    fetchTasks();
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

  const fetchTasks = async () => {
    try {
      const response = await httpClient.get<ApiResponse>(
        `${SERVER_URL}/get_all_tasks`
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

  function getTaskStatus(
    subs_gen_status: string,
    voice_gen_status: string
  ): string {
    const statuses = [subs_gen_status, voice_gen_status];
    const priorities = [
      TaskStatus.processing,
      TaskStatus.queued,
      TaskStatus.idle,
    ];

    for (const priority of priorities) {
      if (statuses.includes(priority)) {
        return priority;
      }
    }
    return "";
  }

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
        {loading ? (
          <div className={styles.loading_tasks_div}>Loading...</div>
        ) : error ? (
          <div>{error}</div>
        ) : (
          <table className={styles.task_table}>
            <thead>
              <tr>
                <th>ID</th>
                <th>Creation Date</th>
                <th>Title</th>
                <th>Last Used</th>
                <th>Lang From</th>
                <th>Lang To</th>
                <th>Creator</th>
                <th>Status</th>
                {/* <th>YT Channel</th> */}
                <th>YT Name</th>
                <th>YT Orig URL</th>
                <th>YT Our URL</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => (
                <tr key={task.number_id}>
                  <td>{task.number_id.toString().padStart(4, "0")}</td>
                  <td>{formatDate(task.creation_date)}</td>
                  <td>
                    <Link key={task.id} to={`/task/${task.id}`}>
                      {task.title}
                    </Link>
                  </td>
                  <td>{formatDate(task.last_used)}</td>
                  <td>{task.lang_from}</td>
                  <td>{task.lang_to}</td>
                  <td>{task.creator_username}</td>
                  <td>
                    {getTaskStatus(
                      task.subs_generation_status,
                      task.voice_generation_status
                    )}
                  </td>
                  {/* <td>{task.yt_channel}</td> */}
                  <td>{task.yt_name}</td>
                  <td>{task.yt_orig_url}</td>
                  <td>{task.yt_our_url}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </ul>
      {isModalOpen && (
        <CreateTaskWindow
          closeWindowFunc={() => setIsModalOpen(false)}
          creatorName={user?.username}
        />
      )}
    </div>
  );
}

export default HomePage;
