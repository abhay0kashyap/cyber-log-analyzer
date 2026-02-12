import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import "./styles.css";

function App() {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="content">
        <Dashboard />
      </div>
    </div>
  );
}

export default App;
