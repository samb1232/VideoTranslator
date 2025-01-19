import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { ErrorPage } from "../pages/errorPage";
import { LoginPage } from "../pages/loginPage";
import { HomePage } from "../pages/homePage";
import { TaskPage, taskPageLoader } from "../pages/taskPage";

export function Router() {
  const router = createBrowserRouter([
    {
      path: "/",
      element: <HomePage />,
      errorElement: <ErrorPage />,
    },
    {
      path: "/login",
      element: <LoginPage />,
      errorElement: <ErrorPage />,
    },
    {
      path: "/task/:taskId",
      element: <TaskPage />,
      errorElement: <ErrorPage />,
      loader: taskPageLoader,
    },
  ]);

  return <RouterProvider router={router} />;
}
