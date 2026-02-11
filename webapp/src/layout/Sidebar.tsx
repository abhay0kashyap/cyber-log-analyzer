import React from "react";
import { FaShieldAlt, FaTachometerAlt, FaExclamationTriangle, FaGlobe, FaFileAlt } from "react-icons/fa";

const Sidebar = () => {
  return (
    <div className="w-64 h-screen bg-panels-cards border-r border-borders p-5" style={{ backgroundColor: 'var(--panels-cards)', borderColor: 'var(--borders)' }}>
      <div className="flex items-center mb-10">
        <FaShieldAlt className="text-accent-intelligence mr-2" size={24} />
        <h1 className="text-xl font-bold text-text-primary">Cyber SIEM</h1>
      </div>
      <nav className="space-y-4">
        <a href="#" className="flex items-center px-4 py-2 text-text-secondary rounded-lg hover:bg-accent-intelligence/10 hover:text-text-primary transition-colors duration-300">
          <FaTachometerAlt className="mr-3" />
          Dashboard
        </a>
        <a href="#" className="flex items-center px-4 py-2 text-text-secondary rounded-lg hover:bg-accent-intelligence/10 hover:text-text-primary transition-colors duration-300">
          <FaExclamationTriangle className="mr-3" />
          Alerts
        </a>
        <a href="#" className="flex items-center px-4 py-2 text-text-secondary rounded-lg hover:bg-accent-intelligence/10 hover:text-text-primary transition-colors duration-300">
          <FaGlobe className="mr-3" />
          Intelligence
        </a>
        <a href="#" className="flex items-center px-4 py-2 text-text-secondary rounded-lg hover:bg-accent-intelligence/10 hover:text-text-primary transition-colors duration-300">
          <FaFileAlt className="mr-3" />
          Reports
        </a>
      </nav>
    </div>
  );
};

export default Sidebar;