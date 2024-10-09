import { formatDate } from "../utils/dateFormatter";
import { TaskDescription } from "../utils/types";

import styles from "./styles/taskItem.module.css";

interface TaskItemProps {
  task: TaskDescription;
}

function TaskItem({ task }: TaskItemProps) {
  return (
    <li className={styles.task_item}>
      <div className={styles.task_content}>
        <div className={styles.task_title}>{task.title}</div>
        <div className={styles.task_date}>{formatDate(task.last_used)}</div>
      </div>
      {/* <button className={styles.delete_button} onClick={handleDelete}>
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className={styles.delete_icon}
        >
          <polyline points="3 6 5 6 21 6"></polyline>
          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
          <line x1="10" y1="11" x2="10" y2="17"></line>
          <line x1="14" y1="11" x2="14" y2="17"></line>
        </svg>
      </button> */}
    </li>
  );
}

export default TaskItem;
