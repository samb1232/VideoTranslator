import { useEffect, useState } from "react";
import httpClient from "../../../shared/api/axiosInstance";

import styles from "./styles/subtitleEditor.module.css";
import { TaskData, TaskStatus } from "../../../entities/task";
import { SERVER_URL } from "../../../shared/const/serverUrl";
import { LoadingAnimBlock } from "../../../entities/loadingAnimBlock";
import { ErrorMessage } from "../../../entities/errorMessage";
import { Subtitle, SubtitleBlock } from "../../../entities/subtitle";

interface SubtitleEditorProps {
  taskData: TaskData;
  fetchTaskFunc: () => Promise<void>;
}

export function SubtitleEditor({
  taskData,
  fetchTaskFunc,
}: SubtitleEditorProps) {
  const [subtitles, setSubtitles] = useState<Subtitle[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [wrongSubsFormat, setWrongSubsFormat] = useState(false);
  const [inputErrors, setInputErrors] = useState<{
    [key: number]: { [key: string]: boolean };
  }>({});
  const processStatus = taskData.voice_generation_status;
  const taskId = taskData.id;

  let subsChanged = true;
  const fetchSubtitles = async () => {
    try {
      const response = await httpClient.get(
        `${SERVER_URL}/get_json_subs/${taskId}`
      );
      if (response.data.status === "success") {
        setSubtitles(response.data.json_subs);
      } else {
        setError(response.data.message);
      }
    } catch (error) {
      setError("Error fetching subtitles");
    }
  };
  useEffect(() => {
    fetchSubtitles();
  }, []);

  useEffect(() => {
    const interval = setInterval(async () => {
      if (subtitles.length == 0) return;
      if (subsChanged) {
        subsChanged = false;
        await saveSubtitles();
      }
    }, 3000); // 10 seconds = 10000 ms

    return () => clearInterval(interval);
  }, [subtitles]);

  function validateField(value: string, field: keyof Subtitle): boolean {
    switch (field) {
      case "start":
      case "end":
        const timePattern = /^\d{2}:\d{2}:\d{2},\d{3}$/;
        return timePattern.test(value);
      case "text":
        return value.trim().length > 0;
      case "speaker":
        const speakerPattern = /^[A-Z]$/;
        return speakerPattern.test(value);
      default:
        return true;
    }
  }

  const saveSubtitles = async () => {
    try {
      const response = await httpClient.post(
        `${SERVER_URL}/save_subs/${taskId}`,
        { json_subs: subtitles }
      );

      if (response.data.status == "success") {
        setWrongSubsFormat(false);
      } else {
        setWrongSubsFormat(true);
      }
    } catch (error) {
      console.error("Error saving subtitles");
    }
  };

  const handleInputChange = (
    index: number,
    field: keyof Subtitle,
    value: string
  ) => {
    const isValid = validateField(value, field);

    const newErrors = { ...inputErrors };

    if (!newErrors[index]) {
      newErrors[index] = {};
    }

    if (isValid) {
      delete newErrors[index]?.[field];
    } else {
      newErrors[index][field] = true;
      setWrongSubsFormat(true);
    }

    setInputErrors(newErrors);

    const newSubtitles = subtitles.map((subtitle, i) =>
      i === index ? { ...subtitle, [field]: value, modified: true } : subtitle
    );

    subsChanged = true;
    setSubtitles(newSubtitles);
  };

  const handleGenerateVoice = async () => {
    try {
      await saveSubtitles();

      if (wrongSubsFormat) return;

      const response = await httpClient.post(
        `${SERVER_URL}/generate_voice/${taskId}`
      );
      if (response.data.status === "success") {
        fetchTaskFunc();
      } else {
        setError(response.data.message);
      }
    } catch (error) {
      setError("Error uploading subtitles and generating voice");
    }
  };

  if (error) {
    return <ErrorMessage error={error} />;
  }

  return (
    <div className={styles.container}>
      {![TaskStatus.queued, TaskStatus.processing].includes(
        processStatus as TaskStatus
      ) && (
        <div className={styles.subtitleList}>
          {subtitles.map((subtitle, index) => (
            <SubtitleBlock
              subtitle={subtitle}
              fieldsErrorMap={inputErrors[index]}
              inputChangeHandler={(fiedsErrorMap, value) =>
                handleInputChange(index, fiedsErrorMap, value)
              }
            />
          ))}
        </div>
      )}
      {taskData.voice_generation_status == TaskStatus.error ? (
        <div className={styles.wrongSubsFormat_div}>
          Last generation process failed. Please check subs and try again.
        </div>
      ) : null}
      {wrongSubsFormat ? (
        <div className={styles.wrongSubsFormat_div}>
          Incorrect subs format! Please check the subs or reload page to reset
          subs.
        </div>
      ) : null}

      <p>Status: {processStatus}</p>
      <LoadingAnimBlock
        isVisible={[TaskStatus.queued, TaskStatus.processing].includes(
          processStatus as TaskStatus
        )}
      >
        <button
          className={styles.button}
          onClick={handleGenerateVoice}
          disabled={
            !taskData.json_translated_subs_path ||
            [TaskStatus.queued, TaskStatus.processing].includes(
              processStatus as TaskStatus
            ) ||
            wrongSubsFormat
          }
        >
          Generate voice
        </button>
      </LoadingAnimBlock>
    </div>
  );
}
