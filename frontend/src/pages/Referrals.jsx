import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import client from '../api/client';
import toast from 'react-hot-toast';
import { Copy, Users, DollarSign, Link2, CheckSquare } from 'lucide-react';

export default function Referrals() {
  const { user } = useAuth();
  const [links, setLinks] = useState([]);
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    client.get('/services').catch(() => {});
  }, []);

  const copyCode = () => {
    navigator.clipboard.writeText(user?.referral_code || '');
    toast.success('Referral code copied!');
  };

  const copyLink = (code) => {
    navigator.clipboard.writeText(`${window.location.origin}/register?ref=${code}`);
    toast.success('Link copied!');
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Referrals & Earnings</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-dark-900 rounded-xl p-6 border border-dark-700">
          <Users className="text-primary-400 mb-2" size={20} />
          <p className="text-dark-400 text-sm">Referral Code</p>
          <div className="flex items-center gap-2 mt-1">
            <p className="text-xl font-bold">{user?.referral_code}</p>
            <button onClick={copyCode} className="text-dark-400 hover:text-primary-400"><Copy size={16} /></button>
          </div>
        </div>
        <div className="bg-dark-900 rounded-xl p-6 border border-dark-700">
          <DollarSign className="text-green-400 mb-2" size={20} />
          <p className="text-dark-400 text-sm">Affiliate Earnings</p>
          <p className="text-xl font-bold">${user?.affiliate_earnings || '0.00'}</p>
        </div>
        <div className="bg-dark-900 rounded-xl p-6 border border-dark-700">
          <DollarSign className="text-purple-400 mb-2" size={20} />
          <p className="text-dark-400 text-sm">Balance</p>
          <p className="text-xl font-bold">${user?.balance || '0.00'}</p>
        </div>
      </div>
      <div className="bg-dark-900 rounded-xl p-6 border border-dark-700 mb-6">
        <h3 className="font-semibold mb-4">How it works</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div className="bg-dark-800 rounded-lg p-4">
            <p className="text-primary-400 font-semibold mb-1">1. Share your code</p>
            <p className="text-dark-400">Share your referral code or link with friends</p>
          </div>
          <div className="bg-dark-800 rounded-lg p-4">
            <p className="text-primary-400 font-semibold mb-1">2. They sign up</p>
            <p className="text-dark-400">When they register using your code</p>
          </div>
          <div className="bg-dark-800 rounded-lg p-4">
            <p className="text-primary-400 font-semibold mb-1">3. You earn</p>
            <p className="text-dark-400">Get 5-10% commission on all their orders</p>
          </div>
        </div>
      </div>
    </div>
  );
}
