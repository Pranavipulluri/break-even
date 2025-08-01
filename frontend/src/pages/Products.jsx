import React, { useState, useEffect } from 'react';
import { Plus, Search, Edit, Trash2, Eye } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import Modal from '../components/common/Modal';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';

const Products = () => {
  const { products, dispatch } = useApp();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  
  const { register, handleSubmit, reset, formState: { errors } } = useForm();

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const response = await api.get('/products');
      dispatch({ type: 'SET_PRODUCTS', payload: response.data });
    } catch (error) {
      toast.error('Failed to fetch products');
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const onSubmit = async (data) => {
    try {
      if (editingProduct) {
        const response = await api.put(`/products/${editingProduct._id}`, data);
        dispatch({ type: 'UPDATE_PRODUCT', payload: response.data });
        toast.success('Product updated successfully');
      } else {
        const response = await api.post('/products', data);
        dispatch({ type: 'ADD_PRODUCT', payload: response.data });
        toast.success('Product created successfully');
      }
      
      setIsModalOpen(false);
      setEditingProduct(null);
      reset();
    } catch (error) {
      toast.error('Failed to save product');
    }
  };

  const handleEdit = (product) => {
    setEditingProduct(product);
    reset(product);
    setIsModalOpen(true);
  };

  const handleDelete = async (productId) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await api.delete(`/products/${productId}`);
        dispatch({ type: 'DELETE_PRODUCT', payload: productId });
        toast.success('Product deleted successfully');
      } catch (error) {
        toast.error('Failed to delete product');
      }
    }
  };

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.category.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Products</h1>
          <p className="text-gray-600 mt-2">Manage your product inventory</p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus size={20} />
          <span>Add Product</span>
        </button>
      </div>

      {/* Search and Filters */}
      <div className="card">
        <div className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <Search size={20} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input-field pl-10"
            />
          </div>
        </div>
      </div>

      {/* Products Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProducts.map((product) => (
          <div key={product._id} className="card hover:shadow-lg transition-shadow">
            <div className="aspect-w-16 aspect-h-9 mb-4">
              <img
                src={product.image || '/api/placeholder/300/200'}
                alt={product.name}
                className="w-full h-48 object-cover rounded-lg"
              />
            </div>
            
            <div className="space-y-2">
              <h3 className="text-lg font-semibold text-gray-900">{product.name}</h3>
              <p className="text-gray-600 text-sm line-clamp-2">{product.description}</p>
              <div className="flex justify-between items-center">
                <span className="text-2xl font-bold text-primary-600">${product.price}</span>
                <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">
                  {product.category}
                </span>
              </div>
              <div className="flex justify-between items-center text-sm text-gray-500">
                <span>Stock: {product.stock}</span>
                <span>SKU: {product.sku}</span>
              </div>
            </div>

            <div className="flex space-x-2 mt-4">
              <button
                onClick={() => handleEdit(product)}
                className="flex-1 btn-secondary flex items-center justify-center space-x-1"
              >
                <Edit size={16} />
                <span>Edit</span>
              </button>
              <button
                onClick={() => handleDelete(product._id)}
                className="flex-1 bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center space-x-1"
              >
                <Trash2 size={16} />
                <span>Delete</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Add/Edit Product Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingProduct(null);
          reset();
        }}
        title={editingProduct ? 'Edit Product' : 'Add New Product'}
      >
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Product Name
            </label>
            <input
              {...register('name', { required: 'Product name is required' })}
              className="input-field"
              placeholder="Enter product name"
            />
            {errors.name && (
              <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              {...register('description', { required: 'Description is required' })}
              rows="3"
              className="input-field"
              placeholder="Enter product description"
            />
            {errors.description && (
              <p className="text-red-500 text-sm mt-1">{errors.description.message}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Price ($)
              </label>
              <input
                type="number"
                step="0.01"
                {...register('price', { required: 'Price is required', min: 0 })}
                className="input-field"
                placeholder="0.00"
              />
              {errors.price && (
                <p className="text-red-500 text-sm mt-1">{errors.price.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Stock Quantity
              </label>
              <input
                type="number"
                {...register('stock', { required: 'Stock is required', min: 0 })}
                className="input-field"
                placeholder="0"
              />
              {errors.stock && (
                <p className="text-red-500 text-sm mt-1">{errors.stock.message}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <select {...register('category', { required: 'Category is required' })} className="input-field">
                <option value="">Select category</option>
                <option value="electronics">Electronics</option>
                <option value="clothing">Clothing</option>
                <option value="food">Food & Beverage</option>
                <option value="books">Books</option>
                <option value="home">Home & Garden</option>
                <option value="other">Other</option>
              </select>
              {errors.category && (
                <p className="text-red-500 text-sm mt-1">{errors.category.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                SKU
              </label>
              <input
                {...register('sku')}
                className="input-field"
                placeholder="Enter SKU"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Product Image URL
            </label>
            <input
              {...register('image')}
              className="input-field"
              placeholder="Enter image URL"
            />
          </div>

          <div className="flex space-x-3 pt-4">
            <button type="submit" className="btn-primary flex-1">
              {editingProduct ? 'Update Product' : 'Add Product'}
            </button>
            <button
              type="button"
              onClick={() => {
                setIsModalOpen(false);
                setEditingProduct(null);
                reset();
              }}
              className="btn-secondary flex-1"
            >
              Cancel
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default Products;
