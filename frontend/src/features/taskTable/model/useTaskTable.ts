import { useState, useEffect } from "react";
import { fetchTasks } from "../api/fetchTasks";
import { TaskData } from "../../../entities/task/model/taskData";
import { TaskStatus } from "../../../entities/task/model/taskStatus";

export function useTaskTable() {
  const [tasks, setTasks] = useState<TaskData[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTasksData();
  }, []);

  async function fetchTasksData() {
    try {
      const response = await fetchTasks();
      if (response.status === "success") {
        setTasks(response.tasks);
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

  return {
    tasks,
    loading,
    error,
    getTaskStatus,
  };
}