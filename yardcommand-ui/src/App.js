import { BrowserRouter as Router, Navigate, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import ClientsList from "./pages/Clients/ClientsList";
import CreateClient from "./pages/Clients/CreateClient";
import BillsPage from "./pages/Bills/BillsPage";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/bills" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Navigate to="/bills" replace />} />

        <Route path="/clients" element={<ClientsList />} />
        <Route path="/clients/create" element={<CreateClient />} />
        <Route path="/bills" element={<BillsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
