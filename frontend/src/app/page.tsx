import { Dashboard } from "@/components/Dashboard";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";

export default function DashboardPage() {
  return (
    <main className="app-shell">
      <Header />
      <Dashboard />
      <Footer />
    </main>
  );
}
