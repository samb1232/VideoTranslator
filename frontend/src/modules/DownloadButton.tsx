import styles from "./styles/downloadButton.module.css";
import { SERVER_URL } from "../utils/serverInfo";
import httpClient from "../utils/httpClient";

interface DownloadButtonProps {
  filepath: string;
  title: string;
}

function DownloadButton({ filepath, title }: DownloadButtonProps) {
  const handleDownload = async () => {
    try {
      const response = await httpClient.get(
        `${SERVER_URL}/api/download/${filepath}`,
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
      console.error("Error downloading the file", error);
    }
  };

  return (
    <button className={styles.button} onClick={handleDownload}>
      {title}
    </button>
  );
}

export default DownloadButton;
