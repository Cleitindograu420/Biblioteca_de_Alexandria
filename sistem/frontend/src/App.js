import { BrowserRouter, Routes, Route } from "react-router-dom";

import Login from "./templates/login";
import Dashboard from "./templates/editar_user";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/Dashboard" element={<Dashboard />} />
      </Routes>
    </BrowserRouter>
  );
}
