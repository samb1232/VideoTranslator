import styles from "./styles/taskTable.module.css";
import { useEffect, useState } from "react";
import { TaskData } from "../../task/taskData";
import { SERVER_URL } from "../../../shared/const/serverUrl";
import httpClient from "../../../shared/api/axiosInstance";
import { ApiResponse } from "../../task/apiResponse";
import { TaskStatus } from "../../task/taskStatus";
import { formatDate } from "../../../shared/utils/dateFormatter";
import { Link } from "react-router-dom";

export function TaskTable() {
  const [tasks, setTasks] = useState<TaskData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTasks();
  }, []);

  async function fetchTasks() {
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
  }

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
    <div>
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
    </div>
  );
}
