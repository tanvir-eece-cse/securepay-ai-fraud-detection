/**
 * Dashboard.tsx - Main analytics dashboard for SecurePay AI
 * 
 * Author: Md. Tanvir Hossain
 * Created: 2025
 * 
 * Note to self: I went with a card-based layout here because it's more
 * intuitive for non-technical bank staff. The color coding (red for fraud,
 * green for safe) follows standard UX conventions I learned during my
 * internship research. StatCard is a custom component I built to keep
 * the main dashboard code clean.
 * 
 * TODO: Add real-time WebSocket updates (currently using mock data)
 */
import { AlertTriangle, Shield, TrendingUp, Activity } from 'lucide-react'

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="mt-1 text-slate-400">Real-time fraud detection overview</p>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Transactions"
          value="12,458"
          change="+12.5%"
          icon={<Activity />}
          color="blue"
        />
        <StatCard
          title="Fraud Detected"
          value="127"
          change="+2.3%"
          icon={<AlertTriangle />}
          color="red"
        />
        <StatCard
          title="Detection Rate"
          value="98.7%"
          change="+0.5%"
          icon={<Shield />}
          color="green"
        />
        <StatCard
          title="Risk Score Avg"
          value="0.23"
          change="-1.2%"
          icon={<TrendingUp />}
          color="yellow"
        />
      </div>

      {/* Recent Alerts */}
      <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-6">
        <h2 className="mb-4 text-xl font-semibold text-white">Recent High-Risk Transactions</h2>
        <div className="space-y-3">
          <AlertItem
            id="TXN-2024-001"
            amount="৳ 95,000"
            risk="High"
            time="2 mins ago"
          />
          <AlertItem
            id="TXN-2024-002"
            amount="৳ 150,000"
            risk="Critical"
            time="15 mins ago"
          />
          <AlertItem
            id="TXN-2024-003"
            amount="৳ 75,000"
            risk="Medium"
            time="32 mins ago"
          />
        </div>
      </div>
    </div>
  )
}

function StatCard({ title, value, change, icon, color }: { title: string; value: string; change: string; icon: React.ReactNode; color: 'blue' | 'red' | 'green' | 'yellow' }) {
  const colors: Record<'blue' | 'red' | 'green' | 'yellow', string> = {
    blue: 'bg-blue-500/10 text-blue-500',
    red: 'bg-red-500/10 text-red-500',
    green: 'bg-green-500/10 text-green-500',
    yellow: 'bg-yellow-500/10 text-yellow-500',
  }

  return (
    <div className="rounded-xl border border-slate-800 bg-slate-800/50 p-6">
      <div className="flex items-center justify-between">
        <div className={`rounded-lg p-3 ${colors[color]}`}>
          {icon}
        </div>
        <span className="text-sm font-medium text-green-500">{change}</span>
      </div>
      <div className="mt-4">
        <p className="text-sm text-slate-400">{title}</p>
        <p className="mt-1 text-2xl font-bold text-white">{value}</p>
      </div>
    </div>
  )
}

function AlertItem({ id, amount, risk, time }: { id: string; amount: string; risk: 'Low' | 'Medium' | 'High' | 'Critical'; time: string }) {
  const riskColors: Record<'Low' | 'Medium' | 'High' | 'Critical', string> = {
    Low: 'bg-green-500/10 text-green-500',
    Medium: 'bg-yellow-500/10 text-yellow-500',
    High: 'bg-orange-500/10 text-orange-500',
    Critical: 'bg-red-500/10 text-red-500',
  }

  return (
    <div className="flex items-center justify-between rounded-lg border border-slate-700 bg-slate-900/50 p-4">
      <div className="flex items-center gap-4">
        <div className="flex flex-col">
          <span className="font-medium text-white">{id}</span>
          <span className="text-sm text-slate-400">{time}</span>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <span className="font-semibold text-white">{amount}</span>
        <span className={`rounded-full px-3 py-1 text-xs font-medium ${riskColors[risk]}`}>
          {risk}
        </span>
      </div>
    </div>
  )
}
