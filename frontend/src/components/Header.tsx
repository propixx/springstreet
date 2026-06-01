import Link from "next/link";

export function Header() {
  return (
    <header className="site-header">
      <div className="site-header-inner">
        <Link className="brand" href="/">
          <span className="brand-mark">ML</span>
          <span>Market Lens</span>
        </Link>

        <nav className="nav-links" aria-label="Main navigation">
          <Link href="/">Dashboard</Link>
          <a href="http://localhost:8000/docs">API Docs</a>
        </nav>
      </div>
    </header>
  );
}
