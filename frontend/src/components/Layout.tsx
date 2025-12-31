import { Outlet, Link, useNavigate } from 'react-router-dom'
import { Shield, LayoutDashboard, CreditCard, BarChart3, LogOut } from 'lucide-react'
import { useAuthStore } from '../store/authStore'

export default function Layout() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-slate-800 bg-slate-900">
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex items-center gap-3 border-b border-slate-800 px-6 py-4">
            <Shield className="h-8 w-8 text-blue-500" />
            <div>
              <h1 className="text-xl font-bold text-white">SecurePay AI</h1>
              <p className="text-xs text-slate-400">Fraud Detection</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-3 py-4">
            <NavLink to="/" icon={<LayoutDashboard />} text="Dashboard" />
            <NavLink to="/transactions" icon={<CreditCard />} text="Transactions" />
            <NavLink to="/analytics" icon={<BarChart3 />} text="Analytics" />
          </nav>

          {/* User Info */}
          <div className="border-t border-slate-800 p-4">
            <div className="mb-3 rounded-lg bg-slate-800 p-3">
              <p className="text-sm font-medium text-white">
                {user?.first_name} {user?.last_name}
              </p>
              <p className="text-xs text-slate-400">{user?.email}</p>
              <p className="mt-1 text-xs text-blue-400">{user?.role}</p>
            </div>
            <button
              onClick={handleLogout}
              className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm text-slate-300 transition-colors hover:bg-slate-800 hover:text-white"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="pl-64">
        <div className="min-h-screen bg-slate-900 p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

function NavLink({ to, icon, text }: { to: string; icon: React.ReactNode; text: string }) {
  return (
    <Link
      to={to}
      className="flex items-center gap-3 rounded-lg px-3 py-2 text-slate-300 transition-colors hover:bg-slate-800 hover:text-white"
    >
      <span className="h-5 w-5">{icon}</span>
      <span className="text-sm font-medium">{text}</span>
    </Link>
  )
}
