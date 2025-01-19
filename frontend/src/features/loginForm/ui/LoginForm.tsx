import styles from "./styles/loginForm.module.css";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { checkAuth, loginUser } from "../api/loginApi";
import { LoadingAnimBlock } from "../../../entities/loadingAnimBlock";
import { ErrorMessage } from "../../../entities/errorMessage";

export function LoginForm() {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [error, setErrorMessage] = useState<string>("");
  const [processing, setProcessing] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try {
      setProcessing(true);
      const response = await loginUser(username, password);

      if (response.status === 200) {
        navigate("/", { replace: true });
      } else {
        setErrorMessage("An error occurred while logging in");
      }
    } catch (error: any) {
      console.error("Error logging in:", error);
      if (error.status === 401) {
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
        const resp = await checkAuth();
        if (resp.data) {
          navigate("/", { replace: true });
        }
      } catch (error) {}
    })();
  }, [navigate]);

  return (
    <form className={styles.login_form} onSubmit={handleSubmit}>
      {error && <ErrorMessage error={error} />}
      <label className={styles.label} htmlFor="username">
        Username:
      </label>
      <input
        type="text"
        value={username}
        id="username"
        className={styles.username_input}
        onChange={(e) => setUsername(e.target.value)}
        required
      />
      <br />
      <br />
      <label className={styles.label} htmlFor="password">
        Password:
      </label>
      <input
        type="password"
        value={password}
        id="password"
        className={styles.password_input}
        onChange={(e) => setPassword(e.target.value)}
        required
      />
      <br />
      <br />
      <LoadingAnimBlock isVisible={processing}>
        <input className={styles.submit_btn} type="submit" value="Login" />
      </LoadingAnimBlock>
    </form>
  );
}
