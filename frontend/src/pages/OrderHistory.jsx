import { useState, useEffect } from 'react';
import { getMyOrders, cancelOrder } from '../api/orders';
import toast from 'react-hot-toast';

export default function OrderHistory() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadOrders(); }, []);

  const loadOrders = async () => {
    setLoading(true);
    try { const res = await getMyOrders(); setOrders(res.data); } catch {} finally { setLoading(false); }
  };

  const handleCancel = async (id) => {
    if (!confirm('Cancel this order?')) return;
    try { await cancelOrder(id); toast.success('Order cancelled'); loadOrders(); } catch (err) { toast.error('Cannot cancel'); }
  };

  const statusColor = (s) => ({
    completed: 'bg-green-500/20 text-green-400',
    in_progress: 'bg-blue-500/20 text-blue-400',
    pending: 'bg-yellow-500/20 text-yellow-400',
    processing: 'bg-orange-500/20 text-orange-400',
    error: 'bg-red-500/20 text-red-400',
    cancelled: 'bg-dark-600 text-dark-400',
  }[s] || 'bg-dark-700 text-dark-400');

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Order History</h2>
      <div className="bg-dark-900 rounded-xl border border-dark-700 overflow-hidden">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-dark-700 text-dark-400">
            <th className="px-4 py-3 text-left">ID</th><th className="px-4 py-3 text-left">Service</th>
            <th className="px-4 py-3 text-left">Quantity</th><th className="px-4 py-3 text-left">Charge</th>
            <th className="px-4 py-3 text-left">Status</th><th className="px-4 py-3 text-left">Progress</th>
            <th className="px-4 py-3 text-left">Actions</th>
          </tr></thead>
          <tbody className="divide-y divide-dark-700">
            {orders.map(o => (
              <tr key={o.id} className="hover:bg-dark-800">
                <td className="px-4 py-3 font-mono text-xs">{o.id.slice(0, 8)}</td>
                <td className="px-4 py-3 max-w-[200px] truncate">{o.target_url}</td>
                <td className="px-4 py-3">{o.quantity}</td>
                <td className="px-4 py-3">${o.charge}</td>
                <td className="px-4 py-3"><span className={`px-2 py-1 rounded-full text-xs ${statusColor(o.status)}`}>{o.status}</span></td>
                <td className="px-4 py-3">{o.current_count}/{o.quantity}</td>
                <td className="px-4 py-3">
                  {['pending', 'processing'].includes(o.status) && (
                    <button onClick={() => handleCancel(o.id)} className="text-red-400 hover:text-red-300 text-xs">Cancel</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {orders.length === 0 && <p className="px-4 py-8 text-center text-dark-400">No orders yet</p>}
      </div>
    </div>
  );
}
