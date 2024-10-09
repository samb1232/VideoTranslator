import React, { useState } from "react";

import styles_loading_anim from "./styles/loading_anim.module.css";
import styles from "./styles/videoUploader.module.css";
import httpClient from "../utils/httpClient";
import { TaskData } from "../utils/taskData";

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
  const [errorMessage, setErrorMessage] = useState("");

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setVideoFile(event.target.files[0]);
    }
  };

  const handleClickButton = async () => {
    setProcessing(true);

    if (!videoFile) {
      setErrorMessage("No video file selected");
      setProcessing(false);
      return;
    }

    try {
      const formData = new FormData();
      formData.append("task_id", taskData.id);
      formData.append("video_file", videoFile);
      formData.append("lang_from", languageFrom);
      formData.append("lang_to", languageTo);

      const response = await httpClient.post(
        "http://localhost:5000/create_subs",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );
      console.log(response);
    } catch (error) {
      console.log(error);
    }

    setProcessing(false);
  };

  return (
    <div className={styles.container}>
      <p className={styles.title}>Upload video .mp4</p>
      {errorMessage != "" && (
        <div className={styles.error_message_div}>{errorMessage}</div>
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
            className={styles.button}
            onClick={handleClickButton}
            disabled={
              videoFile == null ||
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
