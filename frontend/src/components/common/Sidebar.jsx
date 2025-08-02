import React, { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Package, 
  MessageSquare, 
  BarChart3, 
  QrCode, 
  Sparkles, 
  Settings,
  PlusCircle,
  ChevronLeft,
  ChevronRight,
  Users,
  Zap
} from 'lucide-react';

const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const location = useLocation();

  const navItems = [
    { 
      to: '/dashboard', 
      icon: LayoutDashboard, 
      label: 'Dashboard',
      badge: null,
      gradient: 'from-blue-500 to-blue-600'
    },
    { 
      to: '/products', 
      icon: Package, 
      label: 'Products',
      badge: '12',
      gradient: 'from-purple-500 to-purple-600'
    },
    { 
      to: '/messages', 
      icon: MessageSquare, 
      label: 'Messages',
      badge: '3',
      gradient: 'from-green-500 to-green-600'
    },
    { 
      to: '/analytics', 
      icon: BarChart3, 
      label: 'Analytics',
      badge: null,
      gradient: 'from-orange-500 to-orange-600'
    },
    { 
      to: '/qr-code', 
      icon: QrCode, 
      label: 'QR Code',
      badge: null,
      gradient: 'from-indigo-500 to-indigo-600'
    },
    { 
      to: '/ai-tools', 
      icon: Sparkles, 
      label: 'AI Tools',
      badge: 'New',
      gradient: 'from-pink-500 to-pink-600'
    },
    { 
      to: '/website-builder', 
      icon: PlusCircle, 
      label: 'Website Builder',
      badge: null,
      gradient: 'from-teal-500 to-teal-600'
    },
    { 
      to: '/settings', 
      icon: Settings, 
      label: 'Settings',
      badge: null,
      gradient: 'from-gray-500 to-gray-600'
    },
  ];

  const quickActions = [
    { icon: Users, label: 'Add Customer', color: 'text-blue-600' },
    { icon: Package, label: 'Add Product', color: 'text-purple-600' },
    { icon: Zap, label: 'Quick AI', color: 'text-pink-600' },
  ];

  return (
    <>
      {/* Sidebar */}
      <aside className={`fixed left-0 top-16 h-full bg-white/80 backdrop-blur-xl border-r border-white/20 z-40 transition-all duration-300 ${
        isCollapsed ? 'w-16' : 'w-72'
      }`}>
        {/* Toggle Button */}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="absolute -right-3 top-6 w-6 h-6 bg-white border border-gray-200 rounded-full flex items-center justify-center shadow-md hover:shadow-lg transition-all duration-200 hover:scale-110"
        >
          {isCollapsed ? (
            <ChevronRight size={14} className="text-gray-600" />
          ) : (
            <ChevronLeft size={14} className="text-gray-600" />
          )}
        </button>

        <nav className="p-4 space-y-2">
          {/* Navigation Items */}
          {navItems.map((item) => {
            const isActive = location.pathname === item.to;
            
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={`group relative flex items-center space-x-3 px-3 py-3 rounded-xl transition-all duration-200 hover:-translate-y-0.5 ${
                  isActive
                    ? `bg-gradient-to-r ${item.gradient} text-white shadow-lg hover:shadow-xl`
                    : 'text-gray-600 hover:text-gray-900 hover:bg-white/60 hover:shadow-sm'
                }`}
              >
                {/* Icon */}
                <div className={`relative flex-shrink-0 ${isActive ? 'text-white' : 'text-gray-500 group-hover:text-gray-700'}`}>
                  <item.icon size={20} />
                  
                  {/* Active indicator */}
                  {isActive && (
                    <div className="absolute -inset-1 bg-white/20 rounded-lg animate-pulse"></div>
                  )}
                </div>

                {/* Label */}
                {!isCollapsed && (
                  <>
                    <span className="font-medium flex-1">{item.label}</span>
                    
                    {/* Badge */}
                    {item.badge && (
                      <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${
                        isActive 
                          ? 'bg-white/20 text-white' 
                          : item.badge === 'New'
                            ? 'bg-gradient-to-r from-pink-500 to-pink-600 text-white'
                            : 'bg-primary-100 text-primary-700'
                      }`}>
                        {item.badge}
                      </span>
                    )}
                  </>
                )}

                {/* Tooltip for collapsed state */}
                {isCollapsed && (
                  <div className="absolute left-full ml-2 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50">
                    {item.label}
                    {item.badge && (
                      <span className="ml-2 px-1.5 py-0.5 bg-white/20 text-xs rounded-full">
                        {item.badge}
                      </span>
                    )}
                  </div>
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Quick Actions */}
        {!isCollapsed && (
          <div className="px-4 py-6 border-t border-gray-100">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
              Quick Actions
            </h3>
            <div className="space-y-2">
              {quickActions.map((action, index) => (
                <button
                  key={index}
                  className="w-full flex items-center space-x-3 px-3 py-2 text-left text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-all duration-200 hover:translate-x-1"
                >
                  <action.icon size={16} className={action.color} />
                  <span className="text-sm font-medium">{action.label}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Bottom Section */}
        {!isCollapsed && (
          <div className="absolute bottom-4 left-4 right-4">
            <div className="card-gradient p-4 text-center">
              <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-xl mx-auto mb-3 flex items-center justify-center">
                <Sparkles size={20} className="text-white" />
              </div>
              <h4 className="font-semibold text-gray-900 mb-1">Upgrade to Pro</h4>
              <p className="text-xs text-gray-600 mb-3">Unlock advanced AI features</p>
              <button className="w-full btn-primary btn-sm">
                Upgrade Now
              </button>
            </div>
          </div>
        )}
      </aside>

      {/* Backdrop for mobile */}
      <div className={`fixed inset-0 bg-black/20 backdrop-blur-sm z-30 lg:hidden ${
        isCollapsed ? 'hidden' : 'block'
      }`} onClick={() => setIsCollapsed(true)}></div>
    </>
  );
};

export default Sidebar;