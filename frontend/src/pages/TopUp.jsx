import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import client from '../api/client';
import toast from 'react-hot-toast';

export default function TopUp() {
  const { user } = useAuth();
  const [amount, setAmount] = useState('');
  const [method, setMethod] = useState('crypto_usdt');
  const [txRef, setTxRef] = useState('');
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => { client.get('/payments/my').then(res => setPayments(res.data)); }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await client.post('/payments/topup', { amount: parseFloat(amount), method, tx_reference: txRef });
      toast.success('Top-up request submitted!');
      setAmount(''); setTxRef('');
      const res = await client.get('/payments/my');
      setPayments(res.data);
    } catch (err) { toast.error(err.response?.data?.detail || 'Failed'); } finally { setLoading(false); }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Top Up Balance</h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-dark-900 rounded-xl p-6 border border-dark-700">
          <h3 className="font-semibold mb-4">Request Top Up</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input type="number" step="0.01" min="1" placeholder="Amount ($)" value={amount} onChange={e => setAmount(e.target.value)} required
              className="w-full px-4 py-3 bg-dark-800 border border-dark-600 rounded-lg text-dark-100 focus:outline-none focus:border-primary-500" />
            <select value={method} onChange={e => setMethod(e.target.value)}
              className="w-full px-4 py-3 bg-dark-800 border border-dark-600 rounded-lg text-dark-100 focus:outline-none focus:border-primary-500">
              <option value="crypto_usdt">USDT (TRC20)</option>
              <option value="crypto_btc">Bitcoin</option>
              <option value="manual_bank">Bank Transfer</option>
              <option value="manual_other">Other</option>
            </select>
            <input type="text" placeholder="Transaction Reference / Hash" value={txRef} onChange={e => setTxRef(e.target.value)}
              className="w-full px-4 py-3 bg-dark-800 border border-dark-600 rounded-lg text-dark-100 focus:outline-none focus:border-primary-500" />
            <button type="submit" disabled={loading}
              className="w-full py-3 bg-primary-600 hover:bg-primary-700 rounded-lg font-medium disabled:opacity-50">
              {loading ? 'Submitting...' : 'Submit Request'}
            </button>
          </form>
        </div>
        <div className="bg-dark-900 rounded-xl border border-dark-700">
          <div className="px-6 py-4 border-b border-dark-700"><h3 className="font-semibold">Payment History</h3></div>
          <div className="divide-y divide-dark-700 max-h-96 overflow-y-auto">
            {payments.map(p => (
              <div key={p.id} className="px-6 py-4 flex items-center justify-between">
                <div>
                  <p className="text-sm">${p.amount} via {p.method}</p>
                  <p className="text-xs text-dark-400">{new Date(p.created_at).toLocaleDateString()}</p>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs ${
                  p.status === 'approved' ? 'bg-green-500/20 text-green-400' :
                  p.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                  'bg-red-500/20 text-red-400'
                }`}>{p.status}</span>
              </div>
            ))}
            {payments.length === 0 && <p className="px-6 py-8 text-center text-dark-400">No payments yet</p>}
          </div>
        </div>
      </div>
    </div>
  );
}
