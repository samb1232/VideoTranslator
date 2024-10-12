import React, { useEffect, useState } from "react";
import { TaskData } from "../utils/taskData";
import httpClient from "../utils/httpClient";

import styles from "./styles/subtitleEditor.module.css";
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
  const [processing, setProcessing] = useState<boolean>(
    taskData.voice_generation_processing
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
    setProcessing(true);
    try {
      const response = await httpClient.post(
        `${SERVER_URL}/generate_voice/${taskId}`,
        { json_subs: subtitles }
      );
      if (response.data.status === "success") {
        window.location.reload(); // TODO: Make propper refetch
      } else {
        setError(response.data.message);
      }
    } catch (error) {
      setError("Error uploading subtitles and generating voice");
      setProcessing(false);
    }
    setProcessing(false);
  };

  if (error) {
    return <div>{error}</div>;
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
        {processing ? (
          <div className={styles_loading_anim.loader}></div>
        ) : (
          <button
            className={styles_loading_anim.button}
            onClick={handleGenerateVoice}
            disabled={!taskData.json_translated_subs_path || processing}
          >
            Generate voice
          </button>
        )}
      </div>
    </div>
  );
};

export default SubtitleEditor;
