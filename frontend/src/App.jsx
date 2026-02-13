import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Alerts from "./pages/Alerts";
import "./styles.css";

function App() {
  return (
    <Router>
      <div className="app-layout">
        <Sidebar />
        <div className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/alerts" element={<Alerts />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
