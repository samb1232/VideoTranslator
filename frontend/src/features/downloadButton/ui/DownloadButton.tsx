import styles from "./styles/downloadButton.module.css";

import { LoadingAnimBlock } from "../../../entities/loadingAnimBlock";
import { ErrorMessage } from "../../../entities/errorMessage";
import { useDownloadButton } from "../model/useDownloadButton";

interface DownloadButtonProps {
  filepath: string;
  title: string;
}

export function DownloadButton({ filepath, title }: DownloadButtonProps) {
  const { error, processing, handleDownload } = useDownloadButton(filepath);
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
