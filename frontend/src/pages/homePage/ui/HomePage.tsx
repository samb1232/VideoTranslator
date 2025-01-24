import { useEffect } from "react";

import styles from "./styles/home.module.css";
import { TaskTable } from "../../../features/taskTable";
import { CreateNewTaskForm } from "../../../features/createNewTaskForm";
import { useHomePage } from "../model/useHomePage";

export function HomePage() {
  const {
    user,
    isModalOpen,
    setIsModalOpen,
    logoutUser,
    openModal,
    fetchUserInfo,
  } = useHomePage();

  useEffect(() => {
    fetchUserInfo();
  }, []);

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
