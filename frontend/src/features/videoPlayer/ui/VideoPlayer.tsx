import { useEffect, useState } from "react";

import { SERVER_URL } from "../../../shared/const/serverUrl";
import httpClient from "../../../shared/api/axiosInstance";
import { ErrorMessage } from "../../../entities/errorMessage";
import { TaskData } from "../../../entities/task/model/taskData";

interface VideoPlayerProps {
  taskData: TaskData;
}

export function VideoPlayer({ taskData }: VideoPlayerProps) {
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
      {error && <ErrorMessage error={error} />}
      {videoSrc && (
        <video width="640" height="360" controls>
          <source src={videoSrc} type="video/mp4" />
          Your browser does not support the video tag.
        </video>
      )}
    </>
  );
}
