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
import SubtitleEditor from "./SubtitlesEditor";
import VideoPlayer from "./VideoPlayer";

import styles from "./styles/taskPage.module.css";
import { SERVER_URL } from "../utils/serverInfo";

export async function loader({ params }: LoaderFunctionArgs) {
  const taskId = params.taskId;
  const response = await httpClient.get(`${SERVER_URL}/get_task/${taskId}`);
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
        `${SERVER_URL}/delete_task/${taskInfo.id}`
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
      {taskInfo.json_translated_subs_path && (
        <>
          <h1 className={styles.subs_editor_header}>Subtitle Editor</h1>
          <div className={styles.subs_and_video_div}>
            <SubtitleEditor taskData={taskInfo} />

            <div className={styles.video_player_div}>
              {taskInfo.translated_video_path == "" ? (
                <>Video result displays after generating voice</>
              ) : (
                <VideoPlayer taskData={taskInfo} />
              )}
            </div>
          </div>
        </>
      )}

      <div className={styles.results_div}>
        {taskInfo.src_audio_path && <h3>Results:</h3>}
        {taskInfo.translated_audio_path && (
          <DownloadButton
            filepath={taskInfo.translated_audio_path}
            title="Download translated audio"
          />
        )}
        {taskInfo.src_audio_path && (
          <DownloadButton
            filepath={taskInfo.src_audio_path}
            title="Download original audio"
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
      </div>
    </div>
  );
}
