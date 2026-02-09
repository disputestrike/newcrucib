import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  User, Mail, Lock, Bell, Shield, CreditCard, 
  Moon, Sun, Save, Check, AlertCircle
} from 'lucide-react';
import { useAuth } from '../App';

const Settings = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [saved, setSaved] = useState(false);
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    notifications: {
      email: true,
      push: false,
      marketing: false
    }
  });

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'billing', name: 'Billing', icon: CreditCard }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8" data-testid="settings">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Settings</h1>
        <p className="text-gray-400">Manage your account preferences and settings.</p>
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap gap-2">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
              activeTab === tab.id
                ? 'bg-blue-500/20 text-blue-400 border border-blue-500/50'
                : 'bg-white/5 text-gray-400 border border-white/10 hover:border-white/20'
            }`}
            data-testid={`settings-tab-${tab.id}`}
          >
            <tab.icon className="w-4 h-4" />
            {tab.name}
          </button>
        ))}
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 bg-[#0a0a0a] rounded-xl border border-white/10"
        >
          <h3 className="text-lg font-semibold mb-6">Profile Information</h3>
          
          <div className="space-y-6">
            <div className="flex items-center gap-6">
              <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-3xl font-bold">
                {user?.name?.[0]?.toUpperCase() || 'U'}
              </div>
              <div>
                <p className="font-medium">{user?.name}</p>
                <p className="text-sm text-gray-500">{user?.email}</p>
                <p className="text-xs text-gray-600 mt-1">Member since {new Date(user?.created_at).toLocaleDateString()}</p>
              </div>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">Name</label>
                <div className="relative">
                  <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-blue-500 outline-none transition"
                    data-testid="settings-name-input"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Email</label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-blue-500 outline-none transition"
                    data-testid="settings-email-input"
                  />
                </div>
              </div>
            </div>

            <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Current Plan</p>
                  <p className="text-sm text-gray-400 capitalize">{user?.plan || 'Free'}</p>
                </div>
                <a href="/app/tokens" className="text-blue-400 hover:text-blue-300 text-sm">
                  Upgrade Plan →
                </a>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Notifications Tab */}
      {activeTab === 'notifications' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 bg-[#0a0a0a] rounded-xl border border-white/10"
        >
          <h3 className="text-lg font-semibold mb-6">Notification Preferences</h3>
          
          <div className="space-y-4">
            {[
              { key: 'email', label: 'Email Notifications', desc: 'Receive updates about your projects via email' },
              { key: 'push', label: 'Push Notifications', desc: 'Get real-time browser notifications' },
              { key: 'marketing', label: 'Marketing Emails', desc: 'Receive tips, updates, and promotional content' }
            ].map(item => (
              <div key={item.key} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                <div>
                  <p className="font-medium">{item.label}</p>
                  <p className="text-sm text-gray-500">{item.desc}</p>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={formData.notifications[item.key]}
                    onChange={(e) => setFormData({
                      ...formData,
                      notifications: { ...formData.notifications, [item.key]: e.target.checked }
                    })}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-white/10 peer-focus:ring-2 peer-focus:ring-blue-500 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
                </label>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 bg-[#0a0a0a] rounded-xl border border-white/10"
        >
          <h3 className="text-lg font-semibold mb-6">Security Settings</h3>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium mb-2">Current Password</label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="password"
                  className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-blue-500 outline-none transition"
                  placeholder="••••••••"
                />
              </div>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">New Password</label>
                <input
                  type="password"
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-blue-500 outline-none transition"
                  placeholder="••••••••"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Confirm New Password</label>
                <input
                  type="password"
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-blue-500 outline-none transition"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
              <h4 className="font-medium text-red-400 mb-2">Danger Zone</h4>
              <p className="text-sm text-gray-400 mb-4">Once you delete your account, there is no going back.</p>
              <button className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition text-sm">
                Delete Account
              </button>
            </div>
          </div>
        </motion.div>
      )}

      {/* Billing Tab */}
      {activeTab === 'billing' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 bg-[#0a0a0a] rounded-xl border border-white/10"
        >
          <h3 className="text-lg font-semibold mb-6">Billing & Subscription</h3>
          
          <div className="space-y-6">
            <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="font-medium">Current Plan</p>
                  <p className="text-2xl font-bold capitalize text-blue-400">{user?.plan || 'Free'}</p>
                </div>
                <a
                  href="/app/tokens"
                  className="px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg font-medium transition"
                >
                  Upgrade
                </a>
              </div>
              <p className="text-sm text-gray-400">Token balance: {user?.token_balance?.toLocaleString()}</p>
            </div>

            <div>
              <h4 className="font-medium mb-4">Payment Methods</h4>
              <div className="p-4 bg-white/5 rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <CreditCard className="w-6 h-6 text-gray-400" />
                  <span className="text-gray-400">No payment method added</span>
                </div>
                <button className="text-blue-400 hover:text-blue-300 text-sm">
                  Add Method
                </button>
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          className="flex items-center gap-2 px-6 py-3 bg-blue-500 hover:bg-blue-600 rounded-lg font-medium transition"
          data-testid="save-settings-btn"
        >
          {saved ? (
            <>
              <Check className="w-5 h-5" />
              Saved!
            </>
          ) : (
            <>
              <Save className="w-5 h-5" />
              Save Changes
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default Settings;