import { useState } from "react";
import { downloadFile } from "../api/downloadFile";


export function useDownloadButton(filepath: string) {
    const [error, setError] = useState("");
    const [processing, setProcessing] = useState<boolean>(false);

  const handleDownload = async () => {
    try {
      setError("");
      setProcessing(true);
      const fileBlob = await downloadFile(filepath);
      const url = window.URL.createObjectURL(fileBlob);
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

  return {
    error,
    processing,
    handleDownload
  }
}