import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import RecommendPage from "./pages/RecommendPage";
import LoginPage from "./pages/LoginPage";

function App() {
  return (
    <Router>
    <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route
          path="/recommend"
          element={<ProtectedRoute component={<RecommendPage />} />}
        />
    </Routes>
    </Router>
  );
}
function ProtectedRoute({ component }) {
  const searchParams = new URLSearchParams(window.location.search);
  const userId = searchParams.get("user_id");

  if (!userId) {
    return <Navigate to="/" replace />;
  }

  return component;
}
export default App;
