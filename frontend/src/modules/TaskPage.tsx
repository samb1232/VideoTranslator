import { LoaderFunctionArgs, useLoaderData } from "react-router-dom";
import httpClient from "../utils/httpClient";

import styles from "./styles/taskItem.module.css";
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
    console.log(taskInfo);

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
      <h1>{taskInfo.title}</h1>
      <p>ID: {taskInfo.id}</p>
      <p>Title: {taskInfo.title}</p>
      <p>Creation Date: {taskInfo.creation_date}</p>
      <p>Last Used: {taskInfo.last_used}</p>
      <p>Language From: {taskInfo.lang_from}</p>
      <p>Language To: {taskInfo.lang_to}</p>
      <p>Source Video Path: {taskInfo.src_vid_path}</p>
      <p>Source Audio Path: {taskInfo.src_audio_path}</p>
      <p>Source Subs Path: {taskInfo.src_subs_path}</p>
      <p>Translated Subs Path: {taskInfo.translated_subs_path}</p>
      <p>Translated Audio Path: {taskInfo.translated_audio_path}</p>
    </div>
  );
}
