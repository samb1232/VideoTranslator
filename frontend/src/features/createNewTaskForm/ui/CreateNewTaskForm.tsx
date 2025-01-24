import { useState } from "react";
import styles from "./styles/createNewTaskForm.module.css";
import { useCreateNewTask } from "../model/useCreateNewTask";
import { ErrorMessage } from "../../../entities/errorMessage";

interface CreateNewTaskFormProps {
  closeWindowFunc: () => void;
  creatorName: string | undefined;
}

export function CreateNewTaskForm({
  closeWindowFunc,
  creatorName,
}: CreateNewTaskFormProps) {
  const { createTask, isLoading, error, setError } = useCreateNewTask();
  const [newTaskTitle, setNewTaskTitle] = useState("");

  const handleCreateTask = async (event: React.FormEvent) => {
    event.preventDefault();
    if (creatorName === undefined) {
      setError("User is not logged in.");
      return;
    }

    if (newTaskTitle.trim() === "") {
      setError("Task title cannot be empty.");
      return;
    }

    const success = await createTask(newTaskTitle, creatorName);
    if (success) {
      closeWindowFunc();
      setNewTaskTitle("");
    }
  };

  const closeModal = () => {
    closeWindowFunc();
    setNewTaskTitle("");
    setError(null);
  };

  return (
    <div className={styles.modal_overlay}>
      <div className={styles.modal_content}>
        {error && <ErrorMessage error={error} />}
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
              disabled={isLoading}
            />
          </label>
          <button type="submit" disabled={isLoading}>
            {isLoading ? "Creating..." : "Create"}
          </button>
          <button type="button" onClick={closeModal}>
            Cancel
          </button>
        </form>
      </div>
    </div>
  );
}
