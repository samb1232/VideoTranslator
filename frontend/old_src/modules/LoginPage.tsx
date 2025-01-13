import styles from "./styles/login.module.css";
import styles_err_message from "./styles/error_message.module.css";
import styles_loading_anim from "./styles/loading_anim.module.css";

import React, { useEffect, useState } from "react";
import { Form, useNavigate } from "react-router-dom";
import httpClient from "../utils/httpClient";
import { SERVER_URL } from "../utils/serverInfo";

function LoginPage() {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [error, setErrorMessage] = useState("");
  const [processing, setProcessing] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      setProcessing(true);
      const response = await httpClient.post(`${SERVER_URL}/login_user`, {
        username,
        password,
      });

      if (response.status === 200) {
        navigate("/", { replace: true });
      } else {
        setErrorMessage("An error occurred while logging in");
      }
    } catch (error: any) {
      console.error("Error logging in:", error);
      if (error.status == 401) {
        setErrorMessage("Invalid username or password");
      } else {
        setErrorMessage("An error occurred while logging in");
      }
    } finally {
      setProcessing(false);
    }
  };

  useEffect(() => {
    (async () => {
      try {
        const resp = await httpClient.get(`${SERVER_URL}/@me`);
        if (resp.data) {
          navigate("/", { replace: true });
        }
      } catch (error) {}
    })();
  }, []);

  return (
    <div className={styles.login_body}>
      <h1>ExtFo Video Translator</h1>
      <Form className={styles.login_form} onSubmit={handleSubmit}>
        {error != "" && (
          <div className={styles_err_message.error_message_div}>{error}</div>
        )}
        <label htmlFor="username">Username:</label>
        <input
          type="text"
          value={username}
          id="username"
          className={styles.username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <br />
        <br />
        <label htmlFor="password">Password:</label>
        <input
          type="password"
          value={password}
          id="password"
          className={styles.password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <br />
        <br />

        <div className={styles_loading_anim.loader_container}>
          {processing ? (
            <div className={styles_loading_anim.loader}></div>
          ) : (
            <input className={styles.submit_btn} type="submit" value="Login" />
          )}
        </div>
      </Form>
    </div>
  );
}

export default LoginPage;
