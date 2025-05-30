import { useEffect } from "react";
import { Link, useNavigate, useRouteError } from "react-router-dom";

export function ErrorPage() {
  const error: any = useRouteError();
  console.log(error);

  const navigate = useNavigate();
  useEffect(() => {
    if (error.status === 404) navigate("/");
  }, []);

  return (
    <div id="error-page">
      <h1>Oops!</h1>
      <p>Sorry, an unexpected error has occurred.</p>
      <p>
        <i>{error.statusText || error.message}</i>
      </p>
      <Link to={"/"}>Go to the homepage</Link>
    </div>
  );
}
