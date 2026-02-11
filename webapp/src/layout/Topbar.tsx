import React from "react";
import { FaSearch, FaBell, FaUserCircle } from "react-icons/fa";

const Topbar = () => {
  return (
    <div className="h-16 bg-panels-cards border-b border-borders flex items-center justify-between px-6" style={{backgroundColor: 'var(--panels-cards)', borderColor: 'var(--borders)'}}>
      <div className="relative">
        <FaSearch className="absolute top-1/2 left-3 -translate-y-1/2 text-text-muted" />
        <input
          type="text"
          placeholder="Search for alerts, IPs, etc..."
          className="bg-background border border-borders rounded-lg pl-10 pr-4 py-2 text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-intelligence"
          style={{backgroundColor: 'var(--background)', borderColor: 'var(--borders)'}}
        />
      </div>
      <div className="flex items-center space-x-6">
        <button className="text-text-muted hover:text-text-primary">
          <FaBell size={20} />
        </button>
        <div className="flex items-center space-x-2">
          <FaUserCircle size={24} className="text-text-muted" />
          <span className="text-sm text-text-secondary">SOC Analyst</span>
        </div>
      </div>
    </div>
  );
};

export default Topbar;
