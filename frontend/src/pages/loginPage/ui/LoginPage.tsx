import { LoginForm } from "../../../features/loginForm";
import styles from "./styles/loginPage.module.css";

export const LoginPage: React.FC = () => {
  return (
    <div className={styles.login_body}>
      <h1 className={styles.login_title}>ExtFo Video Translator</h1>
      <LoginForm />
    </div>
  );
};
