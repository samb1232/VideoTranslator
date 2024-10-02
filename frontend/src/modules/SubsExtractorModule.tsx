import React, { useState, FormEvent } from "react";
import { Form } from "react-router-dom";

import styles_loading_anim from "./styles/loading_anim.module.css";
import styles_home from "./styles/home.module.css";
import uploadFileToServer from "../utils/fileUploader";

const SubsExtractorModule: React.FC = () => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [sourceLanguage, setSourceLanguage] = useState<string>("en");
  const [processing, setProcessing] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmitToServer = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setProcessing(true);

    if (!videoFile) {
      setErrorMessage("No video file selected");
      setProcessing(false);
      return;
    }

    try {
      const response = await uploadFileToServer(videoFile);
      console.log(response);
    } catch (error) {
      console.log(error);
    }

    setProcessing(false);
  };

  const handleVidFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const target = event.target as HTMLInputElement & { files: FileList };

    if (target.files && target.files.length > 0) {
      const file = target.files[0];
      setVideoFile(file);
    }
  };

  return (
    <div className={styles_home.extract_subs_div}>
      <h3>Extract subtitles from video</h3>
      <Form onSubmit={handleSubmitToServer} encType="multipart/form-data">
        <label>Load the video .mp4 file:</label>
        {errorMessage != "" && (
          <div className={styles_home.error_message_div}>{errorMessage}</div>
        )}
        <input
          type="file"
          name="file"
          accept=".mp4"
          required
          onChange={handleVidFileChange}
        />

        <label>Source language code:</label>

        <input
          type="text"
          id="vid_src_lang"
          name="vid_src_lang"
          value={sourceLanguage}
          required
          onChange={(e) => setSourceLanguage(e.target.value)}
        />
        <div className={styles_loading_anim.loader_container}>
          {processing ? (
            <div className={styles_loading_anim.loader}></div>
          ) : (
            <input
              id="create_subs_button"
              type="submit"
              value="Create subs"
              disabled={videoFile == null || sourceLanguage == ""}
            />
          )}
        </div>
      </Form>
    </div>
  );
};

export default SubsExtractorModule;
