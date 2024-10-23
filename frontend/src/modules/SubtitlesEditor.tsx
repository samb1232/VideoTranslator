import { useEffect, useState } from "react";
import { TaskData, TaskStatus } from "../utils/taskData";
import httpClient from "../utils/httpClient";

import styles from "./styles/subtitleEditor.module.css";
import styles_err_message from "./styles/error_message.module.css";
import styles_loading_anim from "./styles/loading_anim.module.css";
import { SERVER_URL } from "../utils/serverInfo";

interface Subtitle {
  id: number;
  start: string;
  end: string;
  text: string;
  speaker: string;
}

interface SubtitleEditorProps {
  taskData: TaskData;
  fetchTaskFunc: () => Promise<void>;
}

function SubtitleEditor({ taskData, fetchTaskFunc }: SubtitleEditorProps) {
  const [subtitles, setSubtitles] = useState<Subtitle[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [wrongSubsFormat, setWrongSubsFormat] = useState(false);
  const processStatus = taskData.voice_generation_status;
  const taskId = taskData.id;

  let subsChanged = true;

  useEffect(() => {
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
    const newSubtitles = subtitles.map((subtitle, i) =>
      i === index ? { ...subtitle, [field]: value } : subtitle
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
    return <div className={styles_err_message.error_message_div}>{error}</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.subtitleList}>
        {subtitles.map((subtitle, index) => (
          <div key={subtitle.id} className={styles.subtitleItem}>
            <div className={styles.sub_id_div}>{subtitle.id}</div>

            <div className={styles.inputGroup}>
              <div className={styles.speaker_div}>
                <i>Speaker:</i>
                <input
                  type="text"
                  value={subtitle.speaker}
                  onChange={(e) =>
                    handleInputChange(index, "speaker", e.target.value)
                  }
                  className={styles.inputGroup + " " + styles.speaker}
                />
              </div>
              <div className={styles.start_end_time_div}>
                <input
                  type="text"
                  value={subtitle.start}
                  onChange={(e) =>
                    handleInputChange(index, "start", e.target.value)
                  }
                  className={styles.inputGroup}
                />
                <div>→</div>
                <input
                  type="text"
                  value={subtitle.end}
                  onChange={(e) =>
                    handleInputChange(index, "end", e.target.value)
                  }
                  className={styles.inputGroup}
                />
              </div>
            </div>
            <textarea
              value={subtitle.text}
              onChange={(e) => handleInputChange(index, "text", e.target.value)}
              className={styles.textarea}
            />
          </div>
        ))}
      </div>
      {wrongSubsFormat ? (
        <div className={styles.wrongSubsFormat_div}>
          Incorrect subs format! Please check the subs.
        </div>
      ) : null}

      <div className={styles_loading_anim.loader_container}>
        {processStatus != TaskStatus.idle ? (
          <>
            <div>Status: {processStatus}</div>
            <div className={styles_loading_anim.loader}></div>
          </>
        ) : (
          <button
            className={styles_loading_anim.button}
            onClick={handleGenerateVoice}
            disabled={
              !taskData.json_translated_subs_path ||
              processStatus != TaskStatus.idle ||
              wrongSubsFormat
            }
          >
            Generate voice
          </button>
        )}
      </div>
    </div>
  );
}

export default SubtitleEditor;
