import React from 'react';
import { Edit, Trash2, Eye, Package, Star, AlertTriangle, CheckCircle, TrendingUp } from 'lucide-react';

const ProductCard = ({ product, viewMode = 'grid', onEdit, onDelete, onView }) => {
  const getStockStatus = (stock) => {
    if (stock === 0) {
      return { 
        text: 'Out of Stock', 
        color: 'text-red-600 bg-red-100 border-red-200',
        icon: AlertTriangle
      };
    } else if (stock < 10) {
      return { 
        text: 'Low Stock', 
        color: 'text-yellow-600 bg-yellow-100 border-yellow-200',
        icon: AlertTriangle
      };
    } else {
      return { 
        text: 'In Stock', 
        color: 'text-green-600 bg-green-100 border-green-200',
        icon: CheckCircle
      };
    }
  };

  const stockStatus = getStockStatus(product.stock);
  const StatusIcon = stockStatus.icon;

  if (viewMode === 'list') {
    return (
      <div className="card-hover">
        <div className="flex items-center space-x-6">
          {/* Product Image */}
          <div className="w-20 h-20 bg-gradient-to-br from-gray-100 to-gray-200 rounded-xl flex-shrink-0 overflow-hidden">
            {product.image ? (
              <img
                src={product.image}
                alt={product.name}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.src = '/api/placeholder/80/80';
                }}
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center">
                <Package size={24} className="text-gray-400" />
              </div>
            )}
          </div>

          {/* Product Info */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-gray-900 truncate">{product.name}</h3>
                <p className="text-sm text-gray-600 mt-1 line-clamp-2">{product.description}</p>
                <div className="flex items-center space-x-4 mt-2">
                  <span className="text-lg font-bold text-primary-600">${product.price}</span>
                  <span className="badge badge-ghost">{product.category}</span>
                  {product.sku && <span className="text-xs text-gray-500">SKU: {product.sku}</span>}
                </div>
              </div>
              
              <div className="flex items-center space-x-4">
                <div className={`flex items-center space-x-1 px-2 py-1 rounded-full border text-xs font-medium ${stockStatus.color}`}>
                  <StatusIcon size={12} />
                  <span>{stockStatus.text}</span>
                </div>
                <span className="text-sm text-gray-500">Stock: {product.stock}</span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex space-x-2">
            {onView && (
              <button
                onClick={() => onView(product)}
                className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
              >
                <Eye size={16} />
              </button>
            )}
            <button
              onClick={() => onEdit(product)}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Edit size={16} />
            </button>
            <button
              onClick={() => onDelete(product._id)}
              className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <Trash2 size={16} />
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card-hover group overflow-hidden">
      {/* Product Image */}
      <div className="relative aspect-w-16 aspect-h-12 mb-4 overflow-hidden rounded-xl bg-gradient-to-br from-gray-100 to-gray-200">
        {product.image ? (
          <img
            src={product.image}
            alt={product.name}
            className="w-full h-48 object-cover group-hover:scale-105 transition-transform duration-300"
            onError={(e) => {
              e.target.src = '/api/placeholder/300/200';
            }}
          />
        ) : (
          <div className="w-full h-48 flex items-center justify-center">
            <Package size={48} className="text-gray-400" />
          </div>
        )}
        
        {/* Stock Status Badge */}
        <div className="absolute top-3 right-3">
          <div className={`flex items-center space-x-1 px-2 py-1 rounded-full border backdrop-blur-sm text-xs font-medium ${stockStatus.color}`}>
            <StatusIcon size={12} />
            <span>{stockStatus.text}</span>
          </div>
        </div>

        {/* Quick Actions Overlay */}
        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center space-x-2">
          {onView && (
            <button
              onClick={() => onView(product)}
              className="p-2 bg-white/90 backdrop-blur-sm text-gray-700 hover:bg-white rounded-lg transition-colors"
            >
              <Eye size={16} />
            </button>
          )}
          <button
            onClick={() => onEdit(product)}
            className="p-2 bg-white/90 backdrop-blur-sm text-gray-700 hover:bg-white rounded-lg transition-colors"
          >
            <Edit size={16} />
          </button>
        </div>
      </div>
      
      {/* Product Info */}
      <div className="space-y-3">
        <div>
          <h3 className="font-semibold text-gray-900 truncate group-hover:text-primary-600 transition-colors">
            {product.name}
          </h3>
          <p className="text-sm text-gray-600 line-clamp-2 mt-1">
            {product.description}
          </p>
        </div>
        
        <div className="flex items-center justify-between">
          <span className="text-xl font-bold text-primary-600">
            ${product.price}
          </span>
          <div className="flex items-center space-x-2">
            <span className="badge badge-ghost">{product.category}</span>
            {product.stock > 0 && product.stock < 20 && (
              <span className="badge badge-warning">
                <TrendingUp size={10} />
                {product.stock} left
              </span>
            )}
          </div>
        </div>
        
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>Stock: {product.stock}</span>
          {product.sku && <span>SKU: {product.sku}</span>}
        </div>

        {/* Rating/Reviews (if available) */}
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1">
            {[...Array(5)].map((_, i) => (
              <Star 
                key={i} 
                size={12} 
                className={`${i < 4 ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} 
              />
            ))}
          </div>
          <span className="text-xs text-gray-500">(12 reviews)</span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-2 mt-4 pt-4 border-t border-gray-100">
        <button
          onClick={() => onEdit(product)}
          className="flex-1 btn-secondary text-sm"
        >
          <Edit size={14} />
          Edit
        </button>
        
        <button
          onClick={() => onDelete(product._id)}
          className="px-3 py-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors text-sm font-medium"
        >
          <Trash2 size={14} />
        </button>
      </div>
    </div>
  );
};

export default ProductCard;
