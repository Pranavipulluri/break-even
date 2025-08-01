import React from 'react';
import { Edit, Trash2, Eye, Package } from 'lucide-react';

const ProductCard = ({ product, onEdit, onDelete, onView }) => {
  const getStockStatus = (stock) => {
    if (stock === 0) {
      return { text: 'Out of Stock', color: 'text-red-600 bg-red-100' };
    } else if (stock < 10) {
      return { text: 'Low Stock', color: 'text-yellow-600 bg-yellow-100' };
    } else {
      return { text: 'In Stock', color: 'text-green-600 bg-green-100' };
    }
  };

  const stockStatus = getStockStatus(product.stock);

  return (
    <div className="card hover:shadow-lg transition-shadow group">
      {/* Product Image */}
      <div className="aspect-w-16 aspect-h-9 mb-4 relative overflow-hidden rounded-lg bg-gray-100">
        {product.image ? (
          <img
            src={product.image}
            alt={product.name}
            className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-200"
            onError={(e) => {
              e.target.src = '/api/placeholder/300/200';
            }}
          />
        ) : (
          <div className="w-full h-48 flex items-center justify-center bg-gray-200">
            <Package size={48} className="text-gray-400" />
          </div>
        )}
        
        {/* Stock Status Badge */}
        <div className="absolute top-2 right-2">
          <span className={`px-2 py-1 text-xs font-medium rounded-full ${stockStatus.color}`}>
            {stockStatus.text}
          </span>
        </div>
      </div>
      
      {/* Product Info */}
      <div className="space-y-3">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 truncate">
            {product.name}
          </h3>
          <p className="text-gray-600 text-sm line-clamp-2 mt-1">
            {product.description}
          </p>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-2xl font-bold text-primary-600">
            ${product.price}
          </span>
          <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded-full">
            {product.category}
          </span>
        </div>
        
        <div className="flex justify-between items-center text-sm text-gray-500">
          <span>Stock: {product.stock}</span>
          {product.sku && <span>SKU: {product.sku}</span>}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-2 mt-4 pt-4 border-t border-gray-100">
        {onView && (
          <button
            onClick={() => onView(product)}
            className="flex-1 btn-secondary flex items-center justify-center space-x-1 text-sm"
          >
            <Eye size={14} />
            <span>View</span>
          </button>
        )}
        
        <button
          onClick={() => onEdit(product)}
          className="flex-1 btn-secondary flex items-center justify-center space-x-1 text-sm"
        >
          <Edit size={14} />
          <span>Edit</span>
        </button>
        
        <button
          onClick={() => onDelete(product._id)}
          className="flex-1 bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-3 rounded-lg transition-colors flex items-center justify-center space-x-1 text-sm"
        >
          <Trash2 size={14} />
          <span>Delete</span>
        </button>
      </div>
    </div>
  );
};

export default ProductCard;
