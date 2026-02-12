import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import "./styles.css";

function App() {
  return (
    <div className="layout">
      <Sidebar />
      <Dashboard />
    </div>
  );
}

export default App;
