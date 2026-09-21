import { useState, useEffect } from 'react';
import client from '../../api/client';
import toast from 'react-hot-toast';

export default function ManageServices() {
  const [services, setServices] = useState([]);
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    client.get('/services').then(res => setServices(res.data));
    client.get('/services/categories').then(res => setCategories(res.data));
  }, []);

  const toggleService = async (id, isActive) => {
    await client.put(`/services/${id}`, { is_active: !isActive });
    setServices(services.map(s => s.id === id ? {...s, is_active: !isActive} : s));
    toast.success('Updated');
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Manage Services</h2>
      <div className="bg-dark-900 rounded-xl border border-dark-700 overflow-hidden">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-dark-700 text-dark-400">
            <th className="px-4 py-3 text-left">Name</th><th className="px-4 py-3 text-left">Category</th>
            <th className="px-4 py-3 text-left">Price/1K</th><th className="px-4 py-3 text-left">Min-Max</th>
            <th className="px-4 py-3 text-left">Status</th><th className="px-4 py-3 text-left">Actions</th>
          </tr></thead>
          <tbody className="divide-y divide-dark-700">
            {services.map(s => (
              <tr key={s.id} className="hover:bg-dark-800">
                <td className="px-4 py-3 max-w-[300px] truncate">{s.name}</td>
                <td className="px-4 py-3">{categories.find(c => c.id === s.category_id)?.name || '-'}</td>
                <td className="px-4 py-3">${s.price_per_1000}</td>
                <td className="px-4 py-3">{s.min_quantity} - {s.max_quantity}</td>
                <td className="px-4 py-3"><span className={`px-2 py-1 rounded-full text-xs ${s.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>{s.is_active ? 'Active' : 'Inactive'}</span></td>
                <td className="px-4 py-3">
                  <button onClick={() => toggleService(s.id, s.is_active)} className="text-primary-400 hover:text-primary-300 text-xs">{s.is_active ? 'Deactivate' : 'Activate'}</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
