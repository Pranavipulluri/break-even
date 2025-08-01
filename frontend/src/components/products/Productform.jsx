import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { X, Upload } from 'lucide-react';

const ProductForm = ({ product, onSubmit, onCancel, loading = false }) => {
  const { register, handleSubmit, reset, watch, formState: { errors } } = useForm();

  useEffect(() => {
    if (product) {
      reset(product);
    } else {
      reset({
        name: '',
        description: '',
        price: '',
        stock: '',
        category: '',
        sku: '',
        image: ''
      });
    }
  }, [product, reset]);

  const onFormSubmit = (data) => {
    // Convert price and stock to numbers
    const formattedData = {
      ...data,
      price: parseFloat(data.price),
      stock: parseInt(data.stock, 10)
    };
    onSubmit(formattedData);
  };

  const categories = [
    'electronics',
    'clothing',
    'food',
    'books',
    'home',
    'beauty',
    'sports',
    'automotive',
    'toys',
    'other'
  ];

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          {product ? 'Edit Product' : 'Add New Product'}
        </h2>
        <button
          onClick={onCancel}
          className="text-gray-400 hover:text-gray-600 transition-colors"
        >
          <X size={24} />
        </button>
      </div>

      <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
        {/* Product Name */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Product Name *
          </label>
          <input
            {...register('name', { 
              required: 'Product name is required',
              minLength: { value: 2, message: 'Name must be at least 2 characters' }
            })}
            className="input-field"
            placeholder="Enter product name"
          />
          {errors.name && (
            <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>
          )}
        </div>

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description *
          </label>
          <textarea
            {...register('description', { 
              required: 'Description is required',
              minLength: { value: 10, message: 'Description must be at least 10 characters' }
            })}
            rows="4"
            className="input-field"
            placeholder="Describe your product..."
          />
          {errors.description && (
            <p className="text-red-500 text-sm mt-1">{errors.description.message}</p>
          )}
        </div>

        {/* Price and Stock */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Price ($) *
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              {...register('price', { 
                required: 'Price is required',
                min: { value: 0, message: 'Price must be positive' }
              })}
              className="input-field"
              placeholder="0.00"
            />
            {errors.price && (
              <p className="text-red-500 text-sm mt-1">{errors.price.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Stock Quantity *
            </label>
            <input
              type="number"
              min="0"
              {...register('stock', { 
                required: 'Stock quantity is required',
                min: { value: 0, message: 'Stock must be non-negative' }
              })}
              className="input-field"
              placeholder="0"
            />
            {errors.stock && (
              <p className="text-red-500 text-sm mt-1">{errors.stock.message}</p>
            )}
          </div>
        </div>

        {/* Category and SKU */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category *
            </label>
            <select 
              {...register('category', { required: 'Category is required' })} 
              className="input-field"
            >
              <option value="">Select category</option>
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category.charAt(0).toUpperCase() + category.slice(1)}
                </option>
              ))}
            </select>
            {errors.category && (
              <p className="text-red-500 text-sm mt-1">{errors.category.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              SKU (Optional)
            </label>
            <input
              {...register('sku')}
              className="input-field"
              placeholder="Enter SKU"
            />
          </div>
        </div>

        {/* Product Image */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Product Image URL (Optional)
          </label>
          <div className="flex space-x-2">
            <input
              {...register('image')}
              className="input-field flex-1"
              placeholder="https://example.com/image.jpg"
            />
            <button
              type="button"
              className="btn-secondary flex items-center space-x-2"
              onClick={() => {
                // In a real app, this would open a file picker or image upload modal
                alert('Image upload functionality would be implemented here');
              }}
            >
              <Upload size={16} />
              <span>Upload</span>
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            You can provide a direct URL to an image or upload one using the upload button
          </p>
        </div>

        {/* Image Preview */}
        {watch('image') && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Image Preview
            </label>
            <div className="border border-gray-200 rounded-lg p-4">
              <img
                src={watch('image')}
                alt="Product preview"
                className="w-32 h-32 object-cover rounded-lg"
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex space-x-3 pt-6 border-t border-gray-200">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex-1 flex items-center justify-center space-x-2"
          >
            {loading && (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            )}
            <span>{product ? 'Update Product' : 'Add Product'}</span>
          </button>
          
          <button
            type="button"
            onClick={onCancel}
            className="btn-secondary flex-1"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
};

export default ProductForm;