import { useState, useEffect } from 'react';
import { getUsers, updateUser } from '../../api/admin';
import toast from 'react-hot-toast';

export default function ManageUsers() {
  const [users, setUsers] = useState([]);
  const [search, setSearch] = useState('');

  useEffect(() => { loadUsers(); }, []);

  const loadUsers = async (s) => {
    const res = await getUsers(0, 50, s);
    setUsers(res.data);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    loadUsers(search);
  };

  const toggleBan = async (id, isBanned) => {
    await updateUser(id, { is_banned: !isBanned });
    setUsers(users.map(u => u.id === id ? {...u, is_banned: !isBanned} : u));
    toast.success('Updated');
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Manage Users</h2>
      <form onSubmit={handleSearch} className="flex gap-2 mb-6">
        <input type="text" placeholder="Search email/username..." value={search} onChange={e => setSearch(e.target.value)}
          className="flex-1 px-4 py-2 bg-dark-800 border border-dark-600 rounded-lg text-dark-100" />
        <button type="submit" className="px-4 py-2 bg-primary-600 rounded-lg">Search</button>
      </form>
      <div className="bg-dark-900 rounded-xl border border-dark-700 overflow-hidden">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-dark-700 text-dark-400">
            <th className="px-4 py-3 text-left">Username</th><th className="px-4 py-3 text-left">Email</th>
            <th className="px-4 py-3 text-left">Role</th><th className="px-4 py-3 text-left">Balance</th>
            <th className="px-4 py-3 text-left">Status</th><th className="px-4 py-3 text-left">Actions</th>
          </tr></thead>
          <tbody className="divide-y divide-dark-700">
            {users.map(u => (
              <tr key={u.id} className="hover:bg-dark-800">
                <td className="px-4 py-3">{u.username}</td>
                <td className="px-4 py-3">{u.email}</td>
                <td className="px-4 py-3"><span className={`px-2 py-1 rounded-full text-xs ${u.role === 'admin' ? 'bg-purple-500/20 text-purple-400' : 'bg-dark-700 text-dark-400'}`}>{u.role}</span></td>
                <td className="px-4 py-3">${u.balance}</td>
                <td className="px-4 py-3"><span className={`px-2 py-1 rounded-full text-xs ${u.is_banned ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>{u.is_banned ? 'Banned' : 'Active'}</span></td>
                <td className="px-4 py-3">
                  <button onClick={() => toggleBan(u.id, u.is_banned)} className="text-red-400 hover:text-red-300 text-xs">{u.is_banned ? 'Unban' : 'Ban'}</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
