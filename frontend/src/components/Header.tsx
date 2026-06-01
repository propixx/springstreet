import Link from "next/link";
import { API_BASE_URL } from "@/lib/constants";

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
          <a href={`${API_BASE_URL}/docs`}>API Docs</a>
        </nav>
      </div>
    </header>
  );
}
