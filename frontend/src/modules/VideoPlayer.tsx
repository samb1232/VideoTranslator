import { useEffect, useState } from "react";
import httpClient from "../utils/httpClient";
import { TaskData } from "../utils/taskData";
import { SERVER_URL } from "../utils/serverInfo";

interface VideoPlayerProps {
  taskData: TaskData;
}

function VideoPlayer({ taskData }: VideoPlayerProps) {
  const [videoSrc, setVideoSrc] = useState("");

  useEffect(() => {
    const fetchVideo = async () => {
      try {
        if (taskData.translated_video_path == "") return;
        const video_filepath = taskData.translated_video_path;

        const response = await httpClient.get(
          `${SERVER_URL}/api/get_video/${video_filepath}`,
          {
            responseType: "blob",
          }
        );
        console.log(response);

        const videoUrl = URL.createObjectURL(response.data);
        setVideoSrc(videoUrl);
      } catch (error) {
        console.error("Error fetching the video:", error);
      }
    };

    fetchVideo();
  }, []);

  return (
    <>
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
