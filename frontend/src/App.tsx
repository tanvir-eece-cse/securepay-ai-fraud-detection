/**
 * SecurePay AI - Main App Component
 * 
 * @author Md. Tanvir Hossain
 * @description Main routing setup for the fraud detection dashboard
 * 
 * I kept the routing simple here - just login, dashboard, transactions and analytics.
 * The auth check happens at the route level which feels cleaner than 
 * wrapping everything in a context provider.
 */

import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/Layout'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Transactions from './pages/Transactions'
import Analytics from './pages/Analytics'
import './App.css'

function App() {
  const { isAuthenticated } = useAuthStore()

  // Simple auth-based routing - redirect to login if not authenticated
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          isAuthenticated ? <Layout /> : <Navigate to="/login" replace />
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="transactions" element={<Transactions />} />
        <Route path="analytics" element={<Analytics />} />
      </Route>
      {/* Catch all - redirect to home */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
