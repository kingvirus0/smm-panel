import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register, login, getMe } from '../api/auth';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function Register() {
  const [form, setForm] = useState({ email: '', username: '', password: '', referral_code: '' });
  const [loading, setLoading] = useState(false);
  const { loginUser } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await register(form);
      const loginRes = await login(form.email, form.password);
      localStorage.setItem('access_token', loginRes.data.access_token);
      localStorage.setItem('refresh_token', loginRes.data.refresh_token);
      const me = await getMe();
      loginUser(me.data);
      toast.success('Account created!');
      navigate('/');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-950 p-4">
      <div className="w-full max-w-md bg-dark-900 rounded-2xl p-8 border border-dark-700">
        <h1 className="text-2xl font-bold text-center mb-6 text-primary-500">Create Account</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="email" placeholder="Email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} required
            className="w-full px-4 py-3 bg-dark-800 border border-dark-600 rounded-lg text-dark-100 focus:outline-none focus:border-primary-500" />
          <input type="text" placeholder="Username" value={form.username} onChange={e => setForm({...form, username: e.target.value})} required
            className="w-full px-4 py-3 bg-dark-800 border border-dark-600 rounded-lg text-dark-100 focus:outline-none focus:border-primary-500" />
          <input type="password" placeholder="Password" value={form.password} onChange={e => setForm({...form, password: e.target.value})} required
            className="w-full px-4 py-3 bg-dark-800 border border-dark-600 rounded-lg text-dark-100 focus:outline-none focus:border-primary-500" />
          <input type="text" placeholder="Referral code (optional)" value={form.referral_code} onChange={e => setForm({...form, referral_code: e.target.value})}
            className="w-full px-4 py-3 bg-dark-800 border border-dark-600 rounded-lg text-dark-100 focus:outline-none focus:border-primary-500" />
          <button type="submit" disabled={loading}
            className="w-full py-3 bg-primary-600 hover:bg-primary-700 rounded-lg font-medium disabled:opacity-50">
            {loading ? 'Creating...' : 'Create Account'}
          </button>
        </form>
        <p className="text-center text-dark-400 mt-4 text-sm">Already have an account? <Link to="/login" className="text-primary-400 hover:underline">Sign in</Link></p>
      </div>
    </div>
  );
}
