import { useState, useEffect } from 'react';
import { getAllOrders } from '../../api/orders';
import client from '../../api/client';
import toast from 'react-hot-toast';

export default function ManageOrders() {
  const [orders, setOrders] = useState([]);
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => { loadOrders(); }, [statusFilter]);

  const loadOrders = async () => {
    const res = await getAllOrders(0, 50, statusFilter || undefined);
    setOrders(res.data);
  };

  const refundOrder = async (id) => {
    if (!confirm('Refund this order?')) return;
    try {
      await client.post(`/orders/${id}/refund`);
      toast.success('Refunded');
      loadOrders();
    } catch (err) { toast.error('Failed'); }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">All Orders</h2>
      <div className="flex gap-2 mb-6">
        {['', 'pending', 'processing', 'in_progress', 'completed', 'error', 'cancelled'].map(s => (
          <button key={s} onClick={() => setStatusFilter(s)}
            className={`px-3 py-1 rounded-lg text-xs ${statusFilter === s ? 'bg-primary-600 text-white' : 'bg-dark-800 text-dark-400'}`}>
            {s || 'All'}
          </button>
        ))}
      </div>
      <div className="bg-dark-900 rounded-xl border border-dark-700 overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-dark-700 text-dark-400">
            <th className="px-4 py-3 text-left">ID</th><th className="px-4 py-3 text-left">User</th>
            <th className="px-4 py-3 text-left">Target</th><th className="px-4 py-3 text-left">Qty</th>
            <th className="px-4 py-3 text-left">Charge</th><th className="px-4 py-3 text-left">Status</th>
            <th className="px-4 py-3 text-left">Actions</th>
          </tr></thead>
          <tbody className="divide-y divide-dark-700">
            {orders.map(o => (
              <tr key={o.id} className="hover:bg-dark-800">
                <td className="px-4 py-3 font-mono text-xs">{o.id.slice(0, 8)}</td>
                <td className="px-4 py-3 text-xs">{o.user_id?.slice(0, 8)}</td>
                <td className="px-4 py-3 max-w-[200px] truncate">{o.target_url}</td>
                <td className="px-4 py-3">{o.quantity}</td>
                <td className="px-4 py-3">${o.charge}</td>
                <td className="px-4 py-3"><span className={`px-2 py-1 rounded-full text-xs ${
                  o.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                  o.status === 'in_progress' ? 'bg-blue-500/20 text-blue-400' :
                  o.status === 'error' ? 'bg-red-500/20 text-red-400' :
                  'bg-dark-700 text-dark-400'
                }`}>{o.status}</span></td>
                <td className="px-4 py-3">
                  {o.status !== 'refunded' && <button onClick={() => refundOrder(o.id)} className="text-yellow-400 hover:text-yellow-300 text-xs">Refund</button>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
