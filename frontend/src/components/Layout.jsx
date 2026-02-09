import { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, LayoutDashboard, FolderPlus, Coins, FileOutput, 
  Library, Settings, LogOut, Menu, X, ChevronRight,
  Zap, Bell, MessageSquare
} from 'lucide-react';
import { useAuth } from '../App';

const Layout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navigation = [
    { name: 'Dashboard', href: '/app', icon: LayoutDashboard },
    { name: 'New Project', href: '/app/projects/new', icon: FolderPlus },
    { name: 'Token Center', href: '/app/tokens', icon: Coins },
    { name: 'Exports', href: '/app/exports', icon: FileOutput },
    { name: 'Patterns', href: '/app/patterns', icon: Library },
    { name: 'Settings', href: '/app/settings', icon: Settings }
  ];

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const NavItem = ({ item, mobile = false }) => {
    const isActive = location.pathname === item.href;
    return (
      <Link
        to={item.href}
        onClick={() => mobile && setMobileMenuOpen(false)}
        className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
          isActive 
            ? 'bg-blue-500/20 text-blue-400 border-l-2 border-blue-500' 
            : 'text-gray-400 hover:text-white hover:bg-white/5'
        }`}
        data-testid={`nav-${item.name.toLowerCase().replace(' ', '-')}`}
      >
        <item.icon className="w-5 h-5" />
        <span className={`${!sidebarOpen && !mobile ? 'hidden' : ''}`}>{item.name}</span>
      </Link>
    );
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white">
      {/* Mobile Header */}
      <header className="lg:hidden fixed top-0 left-0 right-0 h-16 glass z-50 flex items-center justify-between px-4">
        <Link to="/app" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
            <Sparkles className="w-5 h-5" />
          </div>
          <span className="font-bold">CrucibAI</span>
        </Link>
        <button onClick={() => setMobileMenuOpen(!mobileMenuOpen)} data-testid="mobile-menu-btn">
          {mobileMenuOpen ? <X /> : <Menu />}
        </button>
      </header>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, x: '100%' }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: '100%' }}
            className="lg:hidden fixed inset-0 z-40 bg-[#050505] pt-16"
          >
            <div className="p-4 space-y-2">
              {navigation.map(item => <NavItem key={item.name} item={item} mobile />)}
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-3 px-4 py-3 text-red-400 hover:bg-red-500/10 rounded-lg transition"
                data-testid="mobile-logout-btn"
              >
                <LogOut className="w-5 h-5" />
                <span>Logout</span>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Desktop Sidebar */}
      <aside className={`hidden lg:flex flex-col fixed left-0 top-0 bottom-0 z-40 glass transition-all duration-300 ${
        sidebarOpen ? 'w-64' : 'w-20'
      }`}>
        <div className="h-16 flex items-center justify-between px-4 border-b border-white/10">
          <Link to="/app" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-6 h-6" />
            </div>
            {sidebarOpen && <span className="text-xl font-bold">CrucibAI</span>}
          </Link>
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1 hover:bg-white/10 rounded"
            data-testid="toggle-sidebar-btn"
          >
            <ChevronRight className={`w-5 h-5 transition-transform ${sidebarOpen ? 'rotate-180' : ''}`} />
          </button>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          {navigation.map(item => <NavItem key={item.name} item={item} />)}
        </nav>

        {/* Token Balance */}
        <div className={`p-4 border-t border-white/10 ${!sidebarOpen ? 'hidden' : ''}`}>
          <div className="p-4 bg-blue-500/10 rounded-lg border border-blue-500/30">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">Token Balance</span>
              <Zap className="w-4 h-4 text-blue-400" />
            </div>
            <p className="text-2xl font-bold text-blue-400" data-testid="sidebar-token-balance">
              {user?.token_balance?.toLocaleString() || 0}
            </p>
            <Link 
              to="/app/tokens" 
              className="text-xs text-blue-400 hover:text-blue-300 mt-2 inline-block"
            >
              Buy more tokens →
            </Link>
          </div>
        </div>

        {/* User Section */}
        <div className="p-4 border-t border-white/10">
          <div className={`flex items-center gap-3 ${!sidebarOpen ? 'justify-center' : ''}`}>
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center font-bold">
              {user?.name?.[0]?.toUpperCase() || 'U'}
            </div>
            {sidebarOpen && (
              <div className="flex-1 min-w-0">
                <p className="font-medium truncate" data-testid="sidebar-user-name">{user?.name}</p>
                <p className="text-xs text-gray-500 truncate">{user?.email}</p>
              </div>
            )}
            <button 
              onClick={handleLogout}
              className="p-2 hover:bg-red-500/10 text-gray-400 hover:text-red-400 rounded-lg transition"
              title="Logout"
              data-testid="desktop-logout-btn"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className={`min-h-screen pt-16 lg:pt-0 transition-all duration-300 ${
        sidebarOpen ? 'lg:pl-64' : 'lg:pl-20'
      }`}>
        <div className="p-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default Layout;