import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import client from '../api/client';
import toast from 'react-hot-toast';

const AMOUNTS = [500, 1000, 2000, 5000, 10000];

export default function AddFunds() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [amount, setAmount] = useState('');
  const [provider, setProvider] = useState('');
  const [loading, setLoading] = useState(false);

  const handleInitialize = async (e) => {
    e.preventDefault();
    if (!amount || parseFloat(amount) < 100) {
      toast.error('Minimum amount is ₦100');
      return;
    }
    setLoading(true);
    try {
      let res;
      if (provider === 'paystack') {
        res = await client.post('/payments/paystack/initialize', null, {
          params: { amount_naira: parseFloat(amount) },
        });
        window.open(res.data.authorization_url, '_blank');
        toast.success('Redirecting to Paystack...');
      } else {
        res = await client.post('/payments/flutterwave/initialize', {
          amount_naira: parseFloat(amount),
          email: user.email,
          name: user.username,
        });
        window.open(res.data.payment_link, '_blank');
        toast.success('Redirecting to Flutterwave...');
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Payment failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto">
      <h2 className="text-2xl font-bold mb-6">Add Funds</h2>
      <div className="bg-dark-900 rounded-xl p-6 border border-dark-700">
        <div className="mb-6">
          <p className="text-dark-400 text-sm mb-3">Quick amounts</p>
          <div className="flex flex-wrap gap-2">
            {AMOUNTS.map((a) => (
              <button
                key={a}
                onClick={() => setAmount(String(a))}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  amount === String(a)
                    ? 'bg-primary-600 text-white'
                    : 'bg-dark-800 text-dark-400 hover:text-dark-200'
                }`}
              >
                ₦{a.toLocaleString()}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleInitialize} className="space-y-4">
          <div>
            <label className="block text-sm text-dark-400 mb-1">Amount (NGN)</label>
            <input
              type="number"
              min="100"
              step="100"
              placeholder="Enter amount"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
              className="w-full px-4 py-3 bg-dark-800 border border-dark-600 rounded-lg text-dark-100 focus:outline-none focus:border-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm text-dark-400 mb-2">Payment Method</label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setProvider('paystack')}
                className={`p-4 rounded-lg border text-center transition-colors ${
                  provider === 'paystack'
                    ? 'border-primary-500 bg-primary-600/10 text-primary-400'
                    : 'border-dark-600 bg-dark-800 text-dark-400 hover:border-dark-500'
                }`}
              >
                <p className="font-semibold">Paystack</p>
                <p className="text-xs mt-1">Card / Bank Transfer</p>
              </button>
              <button
                type="button"
                onClick={() => setProvider('flutterwave')}
                className={`p-4 rounded-lg border text-center transition-colors ${
                  provider === 'flutterwave'
                    ? 'border-primary-500 bg-primary-600/10 text-primary-400'
                    : 'border-dark-600 bg-dark-800 text-dark-400 hover:border-dark-500'
                }`}
              >
                <p className="font-semibold">Flutterwave</p>
                <p className="text-xs mt-1">Card / Mobile Money</p>
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !provider || !amount}
            className="w-full py-3 bg-primary-600 hover:bg-primary-700 rounded-lg font-medium disabled:opacity-50"
          >
            {loading ? 'Initializing...' : `Pay ₦${parseFloat(amount || 0).toLocaleString()}`}
          </button>
        </form>

        <div className="mt-6 p-4 bg-dark-800 rounded-lg">
          <p className="text-xs text-dark-400">
            Payment is processed instantly via secure gateway. Your wallet will be credited
            automatically after successful payment. You will receive a Telegram notification.
          </p>
        </div>
      </div>
    </div>
  );
}
