import styles from "./styles/downloadButton.module.css";

import { SERVER_URL } from "../../../shared/const/serverUrl";
import httpClient from "../../../shared/api/axiosInstance";

import { useState } from "react";
import { LoadingAnimBlock } from "../../../entities/loadingAnimBlock";
import { ErrorMessage } from "../../../entities/errorMessage";

interface DownloadButtonProps {
  filepath: string;
  title: string;
}

export function DownloadButton({ filepath, title }: DownloadButtonProps) {
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
    <>
      <LoadingAnimBlock isVisible={processing}>
        <button className={styles.button} onClick={handleDownload}>
          {title}
        </button>
      </LoadingAnimBlock>
      {error != "" && <ErrorMessage error={error} />}
    </>
  );
}
