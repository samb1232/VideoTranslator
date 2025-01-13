import { useState } from "react";
import httpClient from "../utils/httpClient";
import styles from "./styles/modal.module.css";
import styles_err_message from "./styles/error_message.module.css";
import { useNavigate } from "react-router";
import { SERVER_URL } from "../utils/serverInfo";
interface CreateTaskWindowProps {
  closeWindowFunc: () => void;
  creatorName: string | undefined;
}

function CreateTaskWindow({
  closeWindowFunc,
  creatorName,
}: CreateTaskWindowProps) {
  const [newTaskTitle, setNewTaskTitle] = useState("");

  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleCreateTask = async (event: React.FormEvent) => {
    event.preventDefault();
    if (creatorName == undefined) {
      setError("User is not logged in.");
      return;
    }
    try {
      if (newTaskTitle.trim() === "") return;

      const response = await httpClient.post(`${SERVER_URL}/create_task`, {
        title: newTaskTitle,
        creator_username: creatorName,
      });

      if (response.data.status === "success") {
        navigate("/task/" + response.data.task_id);
      } else {
        setError("Failed to create task");
      }
    } catch (error) {
      setError("Error creating task");
    }
  };

  const closeModal = () => {
    closeWindowFunc();
    setNewTaskTitle("");
  };

  return (
    <div className={styles.modal_overlay}>
      <div className={styles.modal_content}>
        {error && (
          <div className={styles_err_message.error_message_div}>{error}</div>
        )}
        <h2>Create New Task</h2>
        <form onSubmit={handleCreateTask}>
          <label>
            Title:
            <input
              type="text"
              name="title"
              value={newTaskTitle}
              onChange={(e) => setNewTaskTitle(e.target.value)}
              required
            />
          </label>
          <button type="submit">Create</button>
          <button type="button" onClick={closeModal}>
            Cancel
          </button>
        </form>
      </div>
    </div>
  );
}

export default CreateTaskWindow;
