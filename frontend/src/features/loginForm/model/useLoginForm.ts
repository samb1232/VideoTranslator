import { useState, useEffect } from "react";
import { useNavigate } from "react-router";
import { loginUser, checkAuth } from "../api/loginApi";

export function useLoginForm() {
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [error, setErrorMessage] = useState<string>("");
  const [processing, setProcessing] = useState<boolean>(false);
  const navigate = useNavigate();

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    try { 
      setProcessing(true);
      setErrorMessage("");
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

  return {
    username,
    password,
    error,
    processing,
    setUsername,
    setPassword,
    handleSubmit,
  };
}