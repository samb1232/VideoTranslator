import {
  Link,
  LoaderFunctionArgs,
  useLoaderData,
  useNavigate,
} from "react-router-dom";

import { SERVER_URL } from "../../../shared/const/serverUrl";
import httpClient from "../../../shared/api/axiosInstance";

import styles from "./styles/taskPage.module.css";
import { useEffect, useState } from "react";
import { VideoUploader } from "../../../features/videoUploader";
import { SubtitleEditor } from "../../../features/subtitlesEditor";
import { VideoPlayer } from "../../../features/videoPlayer";
import { DownloadButton } from "../../../features/downloadButton";
import { TaskData } from "../../../entities/task/model/taskData";
import { TaskStatus } from "../../../entities/task/model/taskStatus";

export async function loader({ params }: LoaderFunctionArgs) {
  const taskId = params.taskId;
  const response = await httpClient.get(`${SERVER_URL}/get_task/${taskId}`);
  if (response.data.status == "success") {
    const taskInfo = response.data.task_info as TaskData;
    return { taskInfo };
  }

  return null;
}

export function TaskPage() {
  const initialTaskInfo = useLoaderData() as { taskInfo: TaskData };
  const [taskInfo, setTaskInfo] = useState(initialTaskInfo.taskInfo);
  const navigate = useNavigate();

  let prevStatus = taskInfo.voice_generation_status;

  async function fetchTaskInfo() {
    try {
      const response = await httpClient.get(
        `${SERVER_URL}/get_task/${taskInfo.id}`
      );

      if (response.data.status === "success") {
        if (
          prevStatus != TaskStatus.idle &&
          response.data.task_info.voice_generation_status == TaskStatus.idle
        ) {
          window.location.reload();
        }
        setTaskInfo(response.data.task_info);
        prevStatus = response.data.task_info.voice_generation_status;
      }
    } catch (error) {
      console.error("Error fetching task info:", error);
    }
  }

  useEffect(() => {
    const getUserInfo = async () => {
      try {
        const resp = await httpClient.get(`${SERVER_URL}/@me`);
        if (!resp.data) {
          navigate("/login", { replace: true });
        }
      } catch (error) {
        navigate("/login", { replace: true });
      }
    };
    getUserInfo();
  }, []);

  useEffect(() => {
    const intervalId = setInterval(fetchTaskInfo, 10000);

    return () => clearInterval(intervalId);
  }, [taskInfo.id]);

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
      <VideoUploader taskData={taskInfo} fetchTaskFunc={fetchTaskInfo} />
      {taskInfo.json_translated_subs_path && (
        <>
          <h1 className={styles.subs_editor_header}>Subtitle Editor</h1>
          <div className={styles.subs_and_video_div}>
            <SubtitleEditor taskData={taskInfo} fetchTaskFunc={fetchTaskInfo} />

            <div className={styles.video_player_div}>
              {taskInfo.translated_video_path != "" && (
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
        {taskInfo.json_translated_subs_path && (
          <DownloadButton
            filepath={taskInfo.json_translated_subs_path}
            title={"Download JSON subs for ChatGPT"}
          />
        )}
      </div>
    </div>
  );
}
