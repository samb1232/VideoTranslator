import styles from "./styles/taskTable.module.css";
import { Link } from "react-router-dom";
import { useTaskTable } from "../model/useTaskTable";
import { formatDate } from "../../../shared/utils/dateFormatter";

export function TaskTable() {
  const { tasks, loading, error, getTaskStatus } = useTaskTable();

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
