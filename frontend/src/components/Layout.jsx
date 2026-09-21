import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { LayoutDashboard, ShoppingCart, Clock, Wallet, Users, Settings, LogOut, Menu, X } from 'lucide-react';
import { useState } from 'react';

const navItems = [
  { to: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/services', icon: ShoppingCart, label: 'Services' },
  { to: '/orders', icon: Clock, label: 'Orders' },
  { to: '/topup', icon: Wallet, label: 'Top Up' },
  { to: '/referrals', icon: Users, label: 'Referrals' },
];

const adminItems = [
  { to: '/admin', icon: Settings, label: 'Admin Dashboard' },
  { to: '/admin/services', icon: Settings, label: 'Manage Services' },
  { to: '/admin/users', icon: Users, label: 'Manage Users' },
  { to: '/admin/orders', icon: Clock, label: 'All Orders' },
];

export default function Layout() {
  const { user, logoutUser } = useAuth();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden">
      <aside className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} fixed inset-y-0 left-0 z-50 w-64 bg-dark-900 border-r border-dark-700 transition-transform lg:translate-x-0 lg:static`}>
        <div className="flex items-center justify-between h-16 px-6 border-b border-dark-700">
          <h1 className="text-xl font-bold text-primary-500">SMM Panel</h1>
          <button onClick={() => setSidebarOpen(false)} className="lg:hidden text-dark-400"><X size={20} /></button>
        </div>
        <nav className="p-4 space-y-1">
          {navItems.map(item => (
            <Link key={item.to} to={item.to} onClick={() => setSidebarOpen(false)}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${location.pathname === item.to ? 'bg-primary-600/20 text-primary-400' : 'text-dark-400 hover:text-dark-200 hover:bg-dark-800'}`}>
              <item.icon size={18} /> {item.label}
            </Link>
          ))}
          {user?.role === 'admin' && (
            <>
              <div className="pt-4 pb-2 px-3 text-xs font-semibold text-dark-500 uppercase">Admin</div>
              {adminItems.map(item => (
                <Link key={item.to} to={item.to} onClick={() => setSidebarOpen(false)}
                  className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${location.pathname === item.to ? 'bg-primary-600/20 text-primary-400' : 'text-dark-400 hover:text-dark-200 hover:bg-dark-800'}`}>
                  <item.icon size={18} /> {item.label}
                </Link>
              ))}
            </>
          )}
        </nav>
        <div className="absolute bottom-0 w-full p-4 border-t border-dark-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-dark-200">{user?.username}</p>
              <p className="text-xs text-dark-500">${user?.balance || '0.00'}</p>
            </div>
            <button onClick={logoutUser} className="text-dark-400 hover:text-red-400"><LogOut size={18} /></button>
          </div>
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto">
        <div className="lg:hidden flex items-center h-16 px-4 border-b border-dark-700">
          <button onClick={() => setSidebarOpen(true)} className="text-dark-400"><Menu size={24} /></button>
          <h1 className="ml-4 text-lg font-bold text-primary-500">SMM Panel</h1>
        </div>
        <div className="p-6"><Outlet /></div>
      </main>
    </div>
  );
}
