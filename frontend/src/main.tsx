import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import ErrorPage from "./modules/ErrorPage.tsx";
import HomePage from "./modules/HomePage.tsx";
import LoginPage from "./modules/LoginPage.tsx";
import TaskPage from "./modules/TaskPage.tsx";
import { loader as taskLoader } from "./modules/TaskPage.tsx";

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
    loader: taskLoader,
  },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);
