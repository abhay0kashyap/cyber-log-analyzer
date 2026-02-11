import React from "react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

interface Props {
  children: React.ReactNode;
}

const MainLayout: React.FC<Props> = ({ children }) => {
  return (
    <div style={{ display: "flex" }}>
      <Sidebar />

      <div
        style={{
          flex: 1,
          background: "#0b1220",
          minHeight: "100vh",
        }}
      >
        <Topbar />

        <div style={{ padding: "40px", color: "white" }}>
          {children}
        </div>
      </div>
    </div>
  );
};

export default MainLayout;
