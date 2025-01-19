import styles from "./styles/errorMessage.module.css";

interface ErrorMessageProps {
  error: string;
}

export function ErrorMessage({ error }: ErrorMessageProps) {
  return <div className={styles.error_message_div}>{error}</div>;
}
