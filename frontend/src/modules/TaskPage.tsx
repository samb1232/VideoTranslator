import {
  Link,
  LoaderFunctionArgs,
  useLoaderData,
  useNavigate,
} from "react-router-dom";
import httpClient from "../utils/httpClient";
import VideoUploader from "./VideoUploader";
import DownloadButton from "./DownloadButton";
import { TaskData } from "../utils/taskData";

import styles from "./styles/taskPage.module.css";

export async function loader({ params }: LoaderFunctionArgs) {
  const taskId = params.taskId;
  const response = await httpClient.get("//localhost:5000/get_task/" + taskId);
  if (response.data.status == "success") {
    const taskInfo = response.data.task_info as TaskData;
    console.log(taskInfo);

    return { taskInfo };
  }

  return null;
}

export default function TaskPage() {
  const { taskInfo } = useLoaderData() as { taskInfo: TaskData };
  const navigate = useNavigate();

  const deleteTask = async () => {
    try {
      if (!window.confirm("Are you sure you want to delete this task?")) return;

      const response = await httpClient.delete(
        "//localhost:5000/delete_task/" + taskInfo.id
      );
      if (response.data.status === "success") {
        navigate("/");
      }
    } catch (error) {
      console.error("Error deleting task:", error);
    }
  };

  if (!taskInfo) {
    return <div>Task not found</div>;
  }

  return (
    <div className={styles.task_body}>
      <Link to="/" className={styles.home_link}>
        Home
      </Link>
      <button onClick={deleteTask} className={styles.delete_task_btn}>
        Delete task
      </button>
      <h1>{taskInfo.title}</h1>
      <VideoUploader taskData={taskInfo} />

      <div className={styles.results_div}>
        <h3>Results:</h3>
        {taskInfo.src_audio_path && (
          <DownloadButton
            filepath={taskInfo.src_audio_path}
            title="Download original audio"
          />
        )}
        {taskInfo.json_translated_subs_path && (
          <DownloadButton
            filepath={taskInfo.json_translated_subs_path}
            title={"Download JSON subs in " + taskInfo.lang_to}
          />
        )}
        {taskInfo.srt_orig_subs_path && (
          <DownloadButton
            filepath={taskInfo.srt_orig_subs_path}
            title={"Download SRT subs in " + taskInfo.lang_from}
          />
        )}
        {taskInfo.srt_translated_subs_path && (
          <DownloadButton
            filepath={taskInfo.srt_translated_subs_path}
            title={"Download SRT subs in " + taskInfo.lang_to}
          />
        )}
        {taskInfo.translated_audio_path && (
          <DownloadButton
            filepath={taskInfo.translated_audio_path}
            title={"Download audio voice in " + taskInfo.lang_to}
          />
        )}
      </div>
    </div>
  );
}
