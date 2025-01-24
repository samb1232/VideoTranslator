import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createTaskApi } from "../api/createTaskApi";

export function useCreateNewTask() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const createTask = async (title: string, creatorName: string): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await createTaskApi(title, creatorName);
      if (response.status === "success") {
        navigate(`/task/${response.task_id}`);
        return true;
      } else {
        setError("Failed to create task");
        return false;
      }
    } catch (err) {
      setError("Error creating task");
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    error,
    setError,
    createTask,
  };
}