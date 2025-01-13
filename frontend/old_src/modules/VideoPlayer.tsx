import { useEffect, useState } from "react";
import httpClient from "../utils/httpClient";
import { TaskData } from "../utils/types";
import { SERVER_URL } from "../utils/serverInfo";
import styles_err_message from "./styles/error_message.module.css";

interface VideoPlayerProps {
  taskData: TaskData;
}

function VideoPlayer({ taskData }: VideoPlayerProps) {
  const [videoSrc, setVideoSrc] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchVideo = async () => {
      try {
        if (taskData.translated_video_path == "") return;
        const video_filepath = taskData.translated_video_path;

        const response = await httpClient.get(
          `${SERVER_URL}/get_video/${video_filepath}`,
          {
            responseType: "blob",
          }
        );

        const videoUrl = URL.createObjectURL(response.data);
        setVideoSrc(videoUrl);
        setError("");
      } catch (error) {
        setError("Error fetching the video");
      }
    };

    fetchVideo();
  }, []);

  return (
    <>
      {error && (
        <div className={styles_err_message.error_message_div}>{error}</div>
      )}
      {videoSrc && (
        <video width="640" height="360" controls>
          <source src={videoSrc} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      )}
    </>
  );
}

export default VideoPlayer;
