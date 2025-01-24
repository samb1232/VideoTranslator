import React, { useState } from "react";
import styles from "./styles/videoUploader.module.css";
import { SERVER_URL } from "../../../shared/const/serverUrl";
import httpClient from "../../../shared/api/axiosInstance";
import { ErrorMessage } from "../../../entities/errorMessage";
import { LoadingAnimBlock } from "../../../entities/loadingAnimBlock";
import { TaskData } from "../../../entities/task/model/taskData";
import { TaskStatus } from "../../../entities/task/model/taskStatus";

const languages = [
  { value: "", label: "Select language" },
  { value: "ru", label: "Russian" },
  { value: "en", label: "English" },
  { value: "es", label: "Spanish" },
  { value: "de", label: "German" },
];

interface VideoUploaderProps {
  taskData: TaskData;
  fetchTaskFunc: () => Promise<void>;
}

export function VideoUploader({ taskData, fetchTaskFunc }: VideoUploaderProps) {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const processStatus = taskData.subs_generation_status;
  const [languageFrom, setLanguageFrom] = useState<string>(taskData.lang_from);
  const [languageTo, setLanguageTo] = useState<string>(taskData.lang_to);
  const [error, setError] = useState("");

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setVideoFile(event.target.files[0]);
    }
  };

  const handleUploadButton = async () => {
    setError("");

    if (!videoFile) {
      setError("No video file selected");
      return;
    }

    if (videoFile.type != "video/mp4") {
      setError("Wrong video format. Try mp4.");
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
      fetchTaskFunc();
    } catch (error) {
      setError(error as string);
    }
  };

  return (
    <div className={styles.container}>
      <p className={styles.title}>Upload video .mp4</p>
      {error != "" && <ErrorMessage error={error} />}
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

      <LoadingAnimBlock
        isVisible={[TaskStatus.queued, TaskStatus.processing].includes(
          processStatus as TaskStatus
        )}
      >
        <button
          className={styles.button}
          onClick={handleUploadButton}
          disabled={
            videoFile == null ||
            languageFrom == "" ||
            languageTo == "" ||
            [TaskStatus.queued, TaskStatus.processing].includes(
              processStatus as TaskStatus
            )
          }
        >
          Create subtitles
        </button>
      </LoadingAnimBlock>
    </div>
  );
}
