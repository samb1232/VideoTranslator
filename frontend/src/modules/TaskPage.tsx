import { Link, LoaderFunctionArgs, useLoaderData } from "react-router-dom";
import httpClient from "../utils/httpClient";

import styles from "./styles/taskPage.module.css";
import VideoUploader from "./VideoUploader";
interface TaskData {
  id: string;
  title: string;
  creation_date: string;
  last_used: string;
  lang_from: string;
  lang_to: string;
  src_vid_path: string;
  src_audio_path: string;
  src_subs_path: string;
  translated_subs_path: string;
  translated_audio_path: string;
}

export async function loader({ params }: LoaderFunctionArgs) {
  const taskId = params.taskId;
  const response = await httpClient.get("//localhost:5000/get_task/" + taskId);
  if (response.data.status == "success") {
    const taskInfo = response.data.task_info as TaskData;

    return { taskInfo };
  }

  return null;
}

export default function TaskPage() {
  const { taskInfo } = useLoaderData() as { taskInfo: TaskData };

  if (!taskInfo) {
    return <div>Task not found</div>;
  }

  return (
    <div className={styles.task_body}>
      <Link to="/" className={styles.home_link}>
        Home
      </Link>
      <h1>{taskInfo.title}</h1>
      <VideoUploader taskId={taskInfo.id} />
    </div>
  );
}
