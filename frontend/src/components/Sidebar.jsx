import { NavLink } from 'react-router-dom';

const navItems = [
  {
    label: 'Dashboard',
    path: '/',
    icon: (
      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.7">
        <path d="M3 12h8V3H3v9Zm10 9h8v-6h-8v6Zm0-8h8V3h-8v10ZM3 21h8v-7H3v7Z" />
      </svg>
    ),
  },
  {
    label: 'Alerts',
    path: '/alerts',
    icon: (
      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.7">
        <path d="M12 9v4m0 4h.01M3.5 18h17L12 3 3.5 18Z" />
      </svg>
    ),
  },
  {
    label: 'Reports',
    path: '/reports',
    icon: (
      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.7">
        <path d="M8 7h8m-8 4h8m-8 4h5M6 3h9l3 3v15H6z" />
      </svg>
    ),
  },
  {
    label: 'Settings',
    path: '/settings',
    icon: (
      <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="1.7">
        <path d="m14.59 4.59 1.82 1.82m-9 9L9.23 17.2m6.54-.01 1.82 1.82M4.59 14.59l1.82 1.82m0-10.64L4.6 7.6m12.8 0 1.82-1.82M12 8.5A3.5 3.5 0 1 1 12 15.5a3.5 3.5 0 0 1 0-7Z" />
      </svg>
    ),
  },
];

function Sidebar() {
  return (
    <aside className="hidden min-h-screen w-64 shrink-0 border-r border-soc-border bg-[#0d1325]/95 px-4 py-5 lg:block">
      <div className="mb-8 rounded-xl border border-soc-border bg-soc-panelSoft px-4 py-3">
        <p className="text-xs font-semibold uppercase tracking-[0.15em] text-soc-muted">SOC Console</p>
        <h2 className="mt-1 text-sm font-semibold text-soc-text">EventLog Analyzer</h2>
      </div>

      <nav className="space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition ${
                isActive
                  ? 'border border-soc-accent/50 bg-soc-accent/15 text-blue-200'
                  : 'border border-transparent text-soc-muted hover:border-soc-border hover:bg-soc-panelSoft hover:text-soc-text'
              }`
            }
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

export default Sidebar;
