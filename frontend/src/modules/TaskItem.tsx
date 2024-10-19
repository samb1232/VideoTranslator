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
    </li>
  );
}

export default TaskItem;
