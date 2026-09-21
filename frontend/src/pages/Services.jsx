import { useState, useEffect } from 'react';
import { getCategories, getServices } from '../api/services';
import { createOrder } from '../api/orders';
import toast from 'react-hot-toast';

export default function Services() {
  const [categories, setCategories] = useState([]);
  const [services, setServices] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [orderForm, setOrderForm] = useState({ service_id: '', target_url: '', quantity: '' });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getCategories().then(res => setCategories(res.data));
    loadServices();
  }, []);

  const loadServices = async (catId) => {
    setSelectedCategory(catId);
    const res = await getServices(catId);
    setServices(res.data);
  };

  const handleOrder = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await createOrder(orderForm);
      toast.success('Order placed!');
      setOrderForm({ service_id: '', target_url: '', quantity: '' });
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Order failed');
    } finally { setLoading(false); }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Services</h2>
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        <button onClick={() => loadServices(null)}
          className={`px-4 py-2 rounded-lg text-sm whitespace-nowrap ${!selectedCategory ? 'bg-primary-600 text-white' : 'bg-dark-800 text-dark-400 hover:text-dark-200'}`}>
          All
        </button>
        {categories.map(cat => (
          <button key={cat.id} onClick={() => loadServices(cat.id)}
            className={`px-4 py-2 rounded-lg text-sm whitespace-nowrap ${selectedCategory === cat.id ? 'bg-primary-600 text-white' : 'bg-dark-800 text-dark-400 hover:text-dark-200'}`}>
            {cat.name}
          </button>
        ))}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {services.map(service => (
          <div key={service.id} className="bg-dark-900 rounded-xl p-6 border border-dark-700">
            <h3 className="font-semibold mb-2 line-clamp-2">{service.name}</h3>
            <div className="text-sm text-dark-400 space-y-1 mb-4">
              <p>Price: <span className="text-primary-400">${service.price_per_1000}/1K</span></p>
              <p>Min: {service.min_quantity} | Max: {service.max_quantity}</p>
              <p>Refill: {service.refill_support ? 'Yes' : 'No'} | Cancel: {service.cancel_support ? 'Yes' : 'No'}</p>
            </div>
            <button onClick={() => { setOrderForm({...orderForm, service_id: service.id}); document.getElementById('order-modal').showModal(); }}
              className="w-full py-2 bg-primary-600 hover:bg-primary-700 rounded-lg text-sm font-medium">
              Order Now
            </button>
          </div>
        ))}
      </div>
      <dialog id="order-modal" className="modal">
        <div className="modal-box bg-dark-900 border border-dark-700">
          <form method="dialog"><button className="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">X</button></form>
          <h3 className="font-bold text-lg mb-4">Place Order</h3>
          <form onSubmit={handleOrder} className="space-y-4">
            <input type="url" placeholder="Target URL (post/video link)" value={orderForm.target_url} onChange={e => setOrderForm({...orderForm, target_url: e.target.value})} required
              className="w-full px-4 py-3 bg-dark-800 border border-dark-600 rounded-lg text-dark-100 focus:outline-none focus:border-primary-500" />
            <input type="number" placeholder="Quantity" value={orderForm.quantity} onChange={e => setOrderForm({...orderForm, quantity: e.target.value})} required min="1"
              className="w-full px-4 py-3 bg-dark-800 border border-dark-600 rounded-lg text-dark-100 focus:outline-none focus:border-primary-500" />
            <button type="submit" disabled={loading}
              className="w-full py-3 bg-primary-600 hover:bg-primary-700 rounded-lg font-medium disabled:opacity-50">
              {loading ? 'Placing...' : 'Place Order'}
            </button>
          </form>
        </div>
        <form method="dialog" className="modal-backdrop"><button>close</button></form>
      </dialog>
    </div>
  );
}
