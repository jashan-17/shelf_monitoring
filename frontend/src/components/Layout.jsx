import { NavLink } from "react-router-dom";

const navigation = [
  { to: "/predict", label: "Live Predict" },
  { to: "/about", label: "About" },
  { to: "/dashboard", label: "Dashboard" },
  { to: "/analytics", label: "Analytics" },
];

function Layout({ children }) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="brand-badge">Shelf Monitoring</div>
          <h1>Classify shelf stock from a live image</h1>
          <p className="sidebar-copy">
            Capture from the device camera or upload a shelf image, run model
            inference, and save the result when you want it recorded.
          </p>
        </div>

        <nav className="nav-list">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                isActive ? "nav-link nav-link-active" : "nav-link"
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <span className="sidebar-footer-label">System Mode</span>
          <strong>Local Development</strong>
        </div>
      </aside>

      <main className="content-area">{children}</main>
    </div>
  );
}

export default Layout;
