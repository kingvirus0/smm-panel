import { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import client from '../api/client';
import toast from 'react-hot-toast';

export default function PaymentVerify() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('checking');
  const [attempts, setAttempts] = useState(0);
  const reference = searchParams.get('reference') || searchParams.get('tx_ref');

  useEffect(() => {
    if (!reference) {
      setStatus('error');
      return;
    }

    const checkPayment = async () => {
      try {
        const res = await client.get('/payments/verify', { params: { ref: reference } });
        if (res.data.status === 'success') {
          setStatus('success');
          toast.success('Payment successful! Wallet credited.');
        } else if (res.data.status === 'pending' && attempts < 10) {
          setAttempts((a) => a + 1);
          setTimeout(checkPayment, 3000);
        } else {
          setStatus('pending');
        }
      } catch {
        if (attempts < 10) {
          setAttempts((a) => a + 1);
          setTimeout(checkPayment, 3000);
        } else {
          setStatus('error');
        }
      }
    };

    checkPayment();
  }, [reference, attempts]);

  if (status === 'checking') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-950">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold mb-2">Verifying Payment...</h2>
          <p className="text-dark-400">Reference: {reference}</p>
          <p className="text-dark-500 text-sm mt-2">Attempt {attempts + 1} of 10</p>
        </div>
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-950">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">✅</div>
          <h2 className="text-2xl font-bold mb-2 text-green-400">Payment Successful!</h2>
          <p className="text-dark-400 mb-6">Your wallet has been credited.</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-primary-600 hover:bg-primary-700 rounded-lg font-medium"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (status === 'pending') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-dark-950">
        <div className="text-center max-w-md">
          <div className="text-6xl mb-4">⏳</div>
          <h2 className="text-2xl font-bold mb-2 text-yellow-400">Still Processing</h2>
          <p className="text-dark-400 mb-2">We're still waiting for confirmation.</p>
          <p className="text-dark-500 text-sm mb-6">Reference: {reference}</p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => navigate('/')}
              className="px-6 py-3 bg-dark-800 hover:bg-dark-700 rounded-lg font-medium"
            >
              Go to Dashboard
            </button>
            <button
              onClick={() => { setAttempts(0); setStatus('checking'); }}
              className="px-6 py-3 bg-primary-600 hover:bg-primary-700 rounded-lg font-medium"
            >
              Check Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-950">
      <div className="text-center max-w-md">
        <div className="text-6xl mb-4">❌</div>
        <h2 className="text-2xl font-bold mb-2 text-red-400">Payment Issue</h2>
        <p className="text-dark-400 mb-2">We couldn't verify your payment.</p>
        <p className="text-dark-500 text-sm mb-6">Reference: {reference}</p>
        <div className="flex gap-3 justify-center">
          <button
            onClick={() => navigate('/addfunds')}
            className="px-6 py-3 bg-primary-600 hover:bg-primary-700 rounded-lg font-medium"
          >
            Try Again
          </button>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-dark-800 hover:bg-dark-700 rounded-lg font-medium"
          >
            Go to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}
