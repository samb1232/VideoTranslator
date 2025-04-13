import { Subtitle } from "../model/subtitle";
import styles from "./styles/subtitleBlock.module.css";

interface SubtitleBlockProps {
  subtitle: Subtitle;
  fieldsErrorMap: { [key: string]: boolean };
  inputChangeHandler: (field: keyof Subtitle, value: string) => void;
}

export function SubtitleBlock({
  subtitle,
  fieldsErrorMap,
  inputChangeHandler,
}: SubtitleBlockProps) {
  return (
    <div key={subtitle.id} className={styles.subtitleItem}>
      <div className={styles.sub_id_div}>
        {subtitle.id}{" "}
        {subtitle.modified && <span className={styles.modified}>*</span>}
      </div>

      <div className={styles.inputGroup}>
        <div className={styles.speaker_div}>
          <i>Speaker:</i>
          <input
            type="text"
            value={subtitle.speaker}
            onChange={(e) => inputChangeHandler("speaker", e.target.value)}
            className={`${styles.inputGroup} ${styles.speaker} ${
              fieldsErrorMap?.speaker ? styles.errorBorder : ""
            }`}
          />
        </div>
        <div className={styles.start_end_time_div}>
          <input
            type="text"
            value={subtitle.start}
            onChange={(e) => inputChangeHandler("start", e.target.value)}
            className={`${styles.inputGroup} ${
              fieldsErrorMap?.start ? styles.errorBorder : ""
            }`}
          />
          <div>→</div>
          <input
            type="text"
            value={subtitle.end}
            onChange={(e) => inputChangeHandler("end", e.target.value)}
            className={`${styles.inputGroup} ${
              fieldsErrorMap?.end ? styles.errorBorder : ""
            }`}
          />
        </div>
      </div>
      <textarea
        value={subtitle.text}
        onChange={(e) => inputChangeHandler("text", e.target.value)}
        className={`${styles.textarea} ${
          fieldsErrorMap?.text ? styles.errorBorder : ""
        }`}
      />
    </div>
  );
}
