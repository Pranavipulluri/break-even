import { useState, useCallback } from 'react';
import { api } from '../services/api';
import toast from 'react-hot-toast';

export const useApi = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const request = useCallback(async (method, url, data = null, options = {}) => {
    try {
      setLoading(true);
      setError(null);

      let response;
      switch (method.toLowerCase()) {
        case 'get':
          response = await api.get(url, options);
          break;
        case 'post':
          response = await api.post(url, data, options);
          break;
        case 'put':
          response = await api.put(url, data, options);
          break;
        case 'delete':
          response = await api.delete(url, options);
          break;
        default:
          throw new Error(`Unsupported method: ${method}`);
      }

      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || 'An error occurred';
      setError(errorMessage);
      
      if (!options.silent) {
        toast.error(errorMessage);
      }
      
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const get = useCallback((url, options = {}) => request('get', url, null, options), [request]);
  const post = useCallback((url, data, options = {}) => request('post', url, data, options), [request]);
  const put = useCallback((url, data, options = {}) => request('put', url, data, options), [request]);
  const del = useCallback((url, options = {}) => request('delete', url, null, options), [request]);

  return {
    loading,
    error,
    get,
    post,
    put,
    delete: del,
    request
  };
};