import client from './client';

export const getServices = (categoryId) => client.get('/services', { params: categoryId ? { category_id: categoryId } : {} });
export const getCategories = () => client.get('/services/categories');
export const getService = (id) => client.get(`/services/${id}`);
