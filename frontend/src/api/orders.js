import client from './client';

export const createOrder = (data) => client.post('/orders', data);
export const createBulkOrders = (orders) => client.post('/orders/bulk', { orders });
export const getMyOrders = (skip = 0, limit = 50) => client.get('/orders', { params: { skip, limit } });
export const getOrder = (id) => client.get(`/orders/${id}`);
export const cancelOrder = (id) => client.post(`/orders/${id}/cancel`);
export const getAllOrders = (skip = 0, limit = 50, status) => client.get('/orders/all', { params: { skip, limit, status } });
