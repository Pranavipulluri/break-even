import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Package, 
  MessageSquare, 
  BarChart3, 
  QrCode, 
  Sparkles, 
  Settings,
  PlusCircle
} from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/products', icon: Package, label: 'Products' },
    { to: '/messages', icon: MessageSquare, label: 'Messages' },
    { to: '/analytics', icon: BarChart3, label: 'Analytics' },
    { to: '/qr-code', icon: QrCode, label: 'QR Code' },
    { to: '/ai-tools', icon: Sparkles, label: 'AI Tools' },
    { to: '/website-builder', icon: PlusCircle, label: 'Website Builder' },
    { to: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <aside className="fixed left-0 top-16 h-full w-64 bg-white border-r border-gray-200 z-40">
      <nav className="p-4">
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                    isActive
                      ? 'bg-primary-50 text-primary-600 border-r-2 border-primary-600'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-800'
                  }`
                }
              >
                <item.icon size={20} />
                <span className="font-medium">{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
};

export default Sidebar;