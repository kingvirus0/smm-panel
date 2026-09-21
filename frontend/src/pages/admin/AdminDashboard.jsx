import { useState, useEffect } from 'react';
import { getDashboard } from '../../api/admin';
import { Users, ShoppingCart, DollarSign, Clock, AlertCircle } from 'lucide-react';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => { getDashboard().then(res => setStats(res.data)); }, []);

  if (!stats) return <div className="flex justify-center py-20"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div></div>;

  const cards = [
    { label: 'Total Users', value: stats.total_users, icon: Users, color: 'text-blue-400' },
    { label: 'New Today', value: stats.new_users_today, icon: Users, color: 'text-green-400' },
    { label: 'Total Orders', value: stats.total_orders, icon: ShoppingCart, color: 'text-purple-400' },
    { label: 'Orders Today', value: stats.orders_today, icon: ShoppingCart, color: 'text-orange-400' },
    { label: 'Revenue Today', value: `$${stats.revenue_today}`, icon: DollarSign, color: 'text-green-400' },
    { label: 'Revenue Week', value: `$${stats.revenue_this_week}`, icon: DollarSign, color: 'text-blue-400' },
    { label: 'Revenue Month', value: `$${stats.revenue_this_month}`, icon: DollarSign, color: 'text-primary-400' },
    { label: 'Pending Payments', value: stats.pending_payments, icon: AlertCircle, color: 'text-yellow-400' },
    { label: 'Active Orders', value: stats.active_orders, icon: Clock, color: 'text-orange-400' },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Admin Dashboard</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {cards.map(c => (
          <div key={c.label} className="bg-dark-900 rounded-xl p-6 border border-dark-700">
            <div className="flex items-center gap-3 mb-2">
              <c.icon className={c.color} size={20} />
              <span className="text-dark-400 text-sm">{c.label}</span>
            </div>
            <p className="text-2xl font-bold">{c.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
