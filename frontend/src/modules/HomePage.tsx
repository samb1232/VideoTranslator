import { useEffect, useState } from "react";
import { User } from "../utils/types";
import { useNavigate } from "react-router-dom";
import httpClient from "../utils/httpClient";
import styles from "./styles/home.module.css";
import SubsExtractorModule from "./SubsExtractorModule";

function HomePage() {
  const [user, setUser] = useState<User | null>(null);

  const navigate = useNavigate();

  const logoutUser = async () => {
    await httpClient.post("//localhost:5000/logout");
    navigate("/login", { replace: true });
  };

  useEffect(() => {
    (async () => {
      try {
        const resp = await httpClient.get("//localhost:5000/@me");
        if (resp.data) {
          setUser(resp.data);
        } else {
          navigate("/login", { replace: true });
        }
      } catch (error) {
        navigate("/login", { replace: true });
      }
    })();
  }, []);

  return (
    <>
      <div className={styles.top_right}>
        <div>Hello, {user?.username}</div>
        <button className={styles.logout_button} onClick={logoutUser}>
          Logout
        </button>
      </div>
      <h1>ExtFo Video Translator</h1>
      <SubsExtractorModule />
    </>
  );
}

export default HomePage;
