import "./App.css";

export default function App() {
  return (
    <div className="dashboard">
      <header className="topbar">
        <h2>Cyber Log Analyzer</h2>
      </header>

      <div className="content">
        <div className="card">
          <h3>Total Events</h3>
          <p>7,333K</p>
        </div>

        <div className="card">
          <h3>Windows Events</h3>
          <p>6,407K</p>
        </div>

        <div className="card">
          <h3>Syslog Events</h3>
          <p>269K</p>
        </div>

        <div className="card">
          <h3>All Devices</h3>
          <p>44</p>
        </div>
      </div>
    </div>
  );
}
