import { useEffect, useState } from "react";

import { SERVER_URL } from "../../../shared/const/serverUrl";
import httpClient from "../../../shared/api/axiosInstance";

import styles from "./styles/subtitleEditor.module.css";
import { TaskData } from "../../../entities/task/taskData";
import { ErrorMessage } from "../../../entities/errorMessage";
import { TaskStatus } from "../../../entities/task/taskStatus";
import { LoadingAnimBlock } from "../../../entities/loadingAnimBlock";

interface Subtitle {
  id: number;
  start: string;
  end: string;
  text: string;
  speaker: string;
  modified: boolean;
}

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
            <div key={subtitle.id} className={styles.subtitleItem}>
              <div className={styles.sub_id_div}>
                {subtitle.id}{" "}
                {subtitle.modified && (
                  <span className={styles.modified}>*</span>
                )}
              </div>

              <div className={styles.inputGroup}>
                <div className={styles.speaker_div}>
                  <i>Speaker:</i>
                  <input
                    type="text"
                    value={subtitle.speaker}
                    onChange={(e) =>
                      handleInputChange(index, "speaker", e.target.value)
                    }
                    className={`${styles.inputGroup} ${styles.speaker} ${
                      inputErrors[index]?.speaker ? styles.errorBorder : ""
                    }`}
                  />
                </div>
                <div className={styles.start_end_time_div}>
                  <input
                    type="text"
                    value={subtitle.start}
                    onChange={(e) =>
                      handleInputChange(index, "start", e.target.value)
                    }
                    className={`${styles.inputGroup} ${
                      inputErrors[index]?.start ? styles.errorBorder : ""
                    }`}
                  />
                  <div>→</div>
                  <input
                    type="text"
                    value={subtitle.end}
                    onChange={(e) =>
                      handleInputChange(index, "end", e.target.value)
                    }
                    className={`${styles.inputGroup} ${
                      inputErrors[index]?.end ? styles.errorBorder : ""
                    }`}
                  />
                </div>
              </div>
              <textarea
                value={subtitle.text}
                onChange={(e) =>
                  handleInputChange(index, "text", e.target.value)
                }
                className={`${styles.textarea} ${
                  inputErrors[index]?.text ? styles.errorBorder : ""
                }`}
              />
            </div>
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
