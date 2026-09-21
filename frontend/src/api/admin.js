import client from './client';

export const getDashboard = () => client.get('/admin/dashboard');
export const getUsers = (skip, limit, search) => client.get('/users', { params: { skip, limit, search } });
export const updateUser = (id, data) => client.put(`/users/${id}`, data);
export const getPendingPayments = () => client.get('/payments/pending');
export const approvePayment = (id, note) => client.put(`/payments/${id}/approve`, null, { params: { admin_note: note } });
export const rejectPayment = (id, note) => client.put(`/payments/${id}/reject`, null, { params: { admin_note: note } });
export const getProviders = () => client.get('/admin/providers');
