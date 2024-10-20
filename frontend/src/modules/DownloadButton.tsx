import styles from "./styles/downloadButton.module.css";
import styles_loading_anim from "./styles/loading_anim.module.css";
import styles_err_message from "./styles/error_message.module.css";
import { SERVER_URL } from "../utils/serverInfo";
import httpClient from "../utils/httpClient";
import { useState } from "react";

interface DownloadButtonProps {
  filepath: string;
  title: string;
}

function DownloadButton({ filepath, title }: DownloadButtonProps) {
  const [error, setError] = useState("");
  const [processing, setProcessing] = useState<boolean>(false);

  const handleDownload = async () => {
    try {
      setError("");
      setProcessing(true);
      const response = await httpClient.get(
        `${SERVER_URL}/download/${filepath}`,
        {
          responseType: "blob",
        }
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", filepath.split("/").pop() || "file");
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      setError("Error downloading the file");
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className={styles_loading_anim.loader_container}>
      {processing ? (
        <div className={styles_loading_anim.loader}></div>
      ) : (
        <button className={styles.button} onClick={handleDownload}>
          {title}
        </button>
      )}
      {error != "" && (
        <div className={styles_err_message.error_message_div}>{error}</div>
      )}
    </div>
  );
}

export default DownloadButton;
