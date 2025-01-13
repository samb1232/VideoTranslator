import { createBrowserRouter, RouterProvider } from "react-router-dom";

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
      loader: taskLoader,
    },
  ]);
  return <RouterProvider router={router} />;
}
