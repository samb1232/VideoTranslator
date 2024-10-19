import React, { useState } from "react";
import httpClient from "../utils/httpClient";
import { TaskData } from "../utils/taskData";

import styles_loading_anim from "./styles/loading_anim.module.css";
import styles_err_message from "./styles/error_message.module.css";
import styles from "./styles/videoUploader.module.css";
import { SERVER_URL } from "../utils/serverInfo";

const languages = [
  { value: "", label: "Select language" },
  { value: "ru", label: "Russian" },
  { value: "en", label: "English" },
  { value: "es", label: "Spanish" },
  { value: "de", label: "German" },
];

interface VideoUploaderProps {
  taskData: TaskData;
}

export default function VideoUploader({ taskData }: VideoUploaderProps) {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState<boolean>(
    taskData.subs_generation_processing
  );
  const [languageFrom, setLanguageFrom] = useState<string>(taskData.lang_from);
  const [languageTo, setLanguageTo] = useState<string>(taskData.lang_to);
  const [error, setError] = useState("");

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setVideoFile(event.target.files[0]);
    }
  };

  const handleUploadButton = async () => {
    setProcessing(true);

    if (!videoFile) {
      setError("No video file selected");
      setProcessing(false);
      return;
    }

    if (videoFile.type != "video/mp4") {
      setError("Wrong video format. Try mp4.");
      setProcessing(false);
      return;
    }

    try {
      setError("");
      const formData = new FormData();
      formData.append("task_id", taskData.id);
      formData.append("video_file", videoFile);
      formData.append("lang_from", languageFrom);
      formData.append("lang_to", languageTo);

      const response = await httpClient.post(
        `${SERVER_URL}/create_subs`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      if (response.data.status === "error") {
        setError(response.data.message);
      }
      setProcessing(false);
      window.location.reload(); // TODO: Make propper refetch
    } catch (error) {
      console.error(error);
      setProcessing(false);
    }
  };

  return (
    <div className={styles.container}>
      <p className={styles.title}>Upload video .mp4</p>
      {error != "" && (
        <div className={styles_err_message.error_message_div}>{error}</div>
      )}
      <input
        type="file"
        accept="video/mp4"
        onChange={handleFileChange}
        className={styles.input}
      />
      <div className={styles.languageSelectors}>
        <label className={styles.label}>
          From:
          <select
            value={languageFrom}
            onChange={(e) => setLanguageFrom(e.target.value)}
            className={styles.select}
          >
            {languages.map((lang) => (
              <option key={lang.value} value={lang.value}>
                {lang.label}
              </option>
            ))}
          </select>
        </label>
        <label className={styles.label}>
          To:
          <select
            value={languageTo}
            onChange={(e) => setLanguageTo(e.target.value)}
            className={styles.select}
          >
            {languages.map((lang) => (
              <option key={lang.value} value={lang.value}>
                {lang.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className={styles_loading_anim.loader_container}>
        {processing ? (
          <div className={styles_loading_anim.loader}></div>
        ) : (
          <button
            className={styles_loading_anim.button}
            onClick={handleUploadButton}
            disabled={
              (videoFile == null && !taskData.src_vid_path) ||
              languageFrom == "" ||
              languageTo == "" ||
              processing
            }
          >
            Create subtitles
          </button>
        )}
      </div>
    </div>
  );
}
