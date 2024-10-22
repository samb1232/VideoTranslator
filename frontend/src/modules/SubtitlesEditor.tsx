import React, { useEffect, useState } from "react";
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
}

const SubtitleEditor: React.FC<SubtitleEditorProps> = ({ taskData }) => {
  const [subtitles, setSubtitles] = useState<Subtitle[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [processStatus, setProcessStatus] = useState<string>(
    taskData.voice_generation_status
  );
  const taskId = taskData.id;

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
  }, [taskData]);

  const handleInputChange = (
    index: number,
    field: keyof Subtitle,
    value: string
  ) => {
    const newSubtitles = subtitles.map((subtitle, i) =>
      i === index ? { ...subtitle, [field]: value } : subtitle
    );
    setSubtitles(newSubtitles);
  };

  const handleGenerateVoice = async () => {
    setProcessStatus(TaskStatus.queued);
    try {
      const response = await httpClient.post(
        `${SERVER_URL}/generate_voice/${taskId}`,
        { json_subs: subtitles }
      );
      if (response.data.status === "success") {
        // TODO: Make propper refetch
      } else {
        setError(response.data.message);
      }
    } catch (error) {
      setError("Error uploading subtitles and generating voice");
      setProcessStatus(TaskStatus.idle);
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
              processStatus != TaskStatus.idle
            }
          >
            Generate voice
          </button>
        )}
      </div>
    </div>
  );
};

export default SubtitleEditor;
