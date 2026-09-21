import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { getMyOrders } from '../api/orders';
import { Wallet, ShoppingCart, Clock, TrendingUp } from 'lucide-react';

export default function Dashboard() {
  const { user } = useAuth();
  const [recentOrders, setRecentOrders] = useState([]);

  useEffect(() => {
    getMyOrders(0, 5).then(res => setRecentOrders(res.data)).catch(() => {});
  }, []);

  const stats = [
    { label: 'Balance', value: `$${user?.balance || '0.00'}`, icon: Wallet, color: 'text-green-400' },
    { label: 'Total Orders', value: recentOrders.length, icon: ShoppingCart, color: 'text-blue-400' },
    { label: 'Referral Earnings', value: `$${user?.affiliate_earnings || '0.00'}`, icon: TrendingUp, color: 'text-purple-400' },
  ];

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Dashboard</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {stats.map(s => (
          <div key={s.label} className="bg-dark-900 rounded-xl p-6 border border-dark-700">
            <div className="flex items-center gap-3 mb-2">
              <s.icon className={s.color} size={20} />
              <span className="text-dark-400 text-sm">{s.label}</span>
            </div>
            <p className="text-2xl font-bold">{s.value}</p>
          </div>
        ))}
      </div>
      <div className="bg-dark-900 rounded-xl border border-dark-700">
        <div className="px-6 py-4 border-b border-dark-700">
          <h3 className="font-semibold">Recent Orders</h3>
        </div>
        <div className="divide-y divide-dark-700">
          {recentOrders.length === 0 ? (
            <p className="px-6 py-4 text-dark-400 text-sm">No orders yet</p>
          ) : recentOrders.map(order => (
            <div key={order.id} className="px-6 py-4 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">{order.target_url}</p>
                <p className="text-xs text-dark-400">Qty: {order.quantity} | ${order.charge}</p>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                order.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                order.status === 'in_progress' ? 'bg-blue-500/20 text-blue-400' :
                order.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                order.status === 'error' ? 'bg-red-500/20 text-red-400' :
                'bg-dark-700 text-dark-400'
              }`}>{order.status}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
