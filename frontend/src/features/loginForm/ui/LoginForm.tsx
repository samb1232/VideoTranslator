import styles from "./styles/loginForm.module.css";
import { useLoginForm } from "../model/useLoginForm";
import { LoadingAnimBlock } from "../../../entities/loadingAnimBlock";
import { ErrorMessage } from "../../../entities/errorMessage";

export function LoginForm() {
  const {
    username,
    password,
    error,
    processing,
    setUsername,
    setPassword,
    handleSubmit,
  } = useLoginForm();

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
