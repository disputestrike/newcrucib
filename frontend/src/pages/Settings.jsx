import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  User, Mail, Lock, Bell, Shield, CreditCard, 
  Moon, Sun, Save, Check, Key, ExternalLink, Zap, HelpCircle, FileText, BarChart3, Settings as SettingsIcon
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { useAuth, API } from '../App';
import axios from 'axios';

const STORAGE_THEME = 'crucibai-theme';

const Settings = () => {
  const { user, token } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [saved, setSaved] = useState(false);
  const [env, setEnv] = useState({});
  const [envSaving, setEnvSaving] = useState(false);
  const [envSaved, setEnvSaved] = useState(false);
  const [theme, setTheme] = useState(() => localStorage.getItem(STORAGE_THEME) || 'system');
  const [language, setLanguage] = useState('en');
  const [formData, setFormData] = useState({
    name: user?.name || '',
    email: user?.email || '',
    notifications: {
      email: true,
      push: false,
      marketing: false,
      taskComplete: true
    }
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') root.classList.add('dark');
    else if (theme === 'light') root.classList.remove('dark');
    else root.classList.toggle('dark', window.matchMedia('(prefers-color-scheme: dark)').matches);
    localStorage.setItem(STORAGE_THEME, theme);
  }, [theme]);
  useEffect(() => {
    if (theme !== 'system') return;
    const m = window.matchMedia('(prefers-color-scheme: dark)');
    const on = () => document.documentElement.classList.toggle('dark', m.matches);
    m.addEventListener('change', on);
    return () => m.removeEventListener('change', on);
  }, [theme]);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  useEffect(() => {
    if (token) {
      axios.get(`${API}/workspace/env`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => setEnv(r.data.env || {}))
        .catch(() => {});
    }
  }, [token]);

  const handleSaveEnv = async () => {
    setEnvSaving(true);
    setEnvSaved(false);
    try {
      await axios.post(`${API}/workspace/env`, { env }, { headers: { Authorization: `Bearer ${token}` } });
      setEnvSaved(true);
      setTimeout(() => setEnvSaved(false), 3000);
    } catch (e) {
      console.error(e);
    } finally {
      setEnvSaving(false);
    }
  };

  const sidebarNav = [
    { id: 'profile', name: 'Account', icon: User },
    { id: 'general', name: 'General', icon: SettingsIcon },
    { id: 'usage', name: 'Usage', icon: BarChart3 },
    { id: 'api', name: 'API & Environment', icon: Key },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'billing', name: 'Billing', icon: CreditCard },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'help', name: 'Get help', icon: HelpCircle }
  ];

  return (
    <div className="flex flex-col md:flex-row gap-8 max-w-5xl" data-testid="settings">
      {/* Left sidebar (Manus-style) */}
      <aside className="md:w-56 shrink-0">
        <h2 className="text-lg font-semibold mb-4">Settings</h2>
        <nav className="space-y-1">
          {sidebarNav.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left transition ${
                activeTab === tab.id
                  ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30'
                  : 'text-gray-400 hover:bg-white/5 hover:text-white border border-transparent'
              }`}
              data-testid={`settings-tab-${tab.id}`}
            >
              <tab.icon className="w-5 h-5 shrink-0" />
              {tab.name}
            </button>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <div className="flex-1 min-w-0 space-y-8">

      {/* General Tab (language + appearance) */}
      {activeTab === 'general' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 bg-[#0a0a0a] rounded-xl border border-white/10"
        >
          <h3 className="text-lg font-semibold mb-6">General</h3>
          <div className="space-y-8">
            <div>
              <label className="block text-sm font-medium mb-2">Language</label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full max-w-xs px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-blue-500 outline-none transition"
              >
                <option value="en">English</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-3">Appearance</label>
              <p className="text-sm text-gray-500 mb-4">Choose how CrucibAI looks. You can pick a theme or follow your system.</p>
              <div className="flex flex-wrap gap-4">
                {[
                  { id: 'light', label: 'Light', icon: Sun, preview: <div className="w-12 h-8 rounded-lg bg-gray-200 border border-gray-300" /> },
                  { id: 'dark', label: 'Dark', icon: Moon, preview: <div className="w-12 h-8 rounded-lg bg-gray-800 border border-gray-600" /> },
                  { id: 'system', label: 'Follow system', icon: Zap, preview: <div className="w-12 h-8 rounded-lg overflow-hidden flex"><div className="w-1/2 h-full bg-gray-800" /><div className="w-1/2 h-full bg-gray-200" /></div> }
                ].map(opt => (
                  <button
                    key={opt.id}
                    type="button"
                    onClick={() => setTheme(opt.id)}
                    className={`flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition ${
                      theme === opt.id
                        ? 'border-blue-500 bg-blue-500/10 text-blue-400'
                        : 'border-white/10 bg-white/5 text-gray-400 hover:border-white/20'
                    }`}
                  >
                    {opt.preview}
                    <span className="text-sm font-medium flex items-center gap-1">
                      <opt.icon className="w-4 h-4" />
                      {opt.label}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Usage Tab */}
      {activeTab === 'usage' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 bg-[#0a0a0a] rounded-xl border border-white/10"
        >
          <h3 className="text-lg font-semibold mb-6">Usage</h3>
          <div className="space-y-6">
            <div className="p-4 bg-white/5 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">Token balance</span>
                <span className="font-mono font-semibold" data-testid="settings-token-balance">
                  {(user?.token_balance ?? 0).toLocaleString()}
                </span>
              </div>
              <p className="text-xs text-gray-500">Prepaid tokens for AI builds. Usage is deducted per request.</p>
            </div>
            <div className="flex flex-wrap gap-3">
              <Link
                to="/app/tokens"
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg font-medium text-sm transition"
              >
                <Zap className="w-4 h-4" /> Buy more tokens
              </Link>
              <Link
                to="/pricing"
                className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/15 rounded-lg font-medium text-sm transition"
              >
                <FileText className="w-4 h-4" /> Pricing plans
              </Link>
            </div>
          </div>
        </motion.div>
      )}

      {/* Get help Tab */}
      {activeTab === 'help' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 bg-[#0a0a0a] rounded-xl border border-white/10"
        >
          <h3 className="text-lg font-semibold mb-6">Get help</h3>
          <div className="space-y-4">
            <a
              href="/learn"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-3 p-4 bg-white/5 rounded-lg hover:bg-white/10 transition"
            >
              <FileText className="w-5 h-5 text-blue-400" />
              <div>
                <p className="font-medium">Documentation</p>
                <p className="text-sm text-gray-500">Guides, shortcuts, and how-tos</p>
              </div>
              <ExternalLink className="w-4 h-4 ml-auto text-gray-500" />
            </a>
            <a
              href="mailto:support@crucibai.com"
              className="flex items-center gap-3 p-4 bg-white/5 rounded-lg hover:bg-white/10 transition"
            >
              <HelpCircle className="w-5 h-5 text-blue-400" />
              <div>
                <p className="font-medium">Contact support</p>
                <p className="text-sm text-gray-500">support@crucibai.com</p>
              </div>
              <ExternalLink className="w-4 h-4 ml-auto text-gray-500" />
            </a>
          </div>
        </motion.div>
      )}

      {/* API & Environment Tab */}
      {activeTab === 'api' && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 bg-[#0a0a0a] rounded-xl border border-white/10"
        >
          <h3 className="text-lg font-semibold mb-2">Workspace environment (API keys)</h3>
          <p className="text-sm text-gray-500 mb-4">Keys are stored per-user and used for AI builds. Never commit keys to git.</p>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">OPENAI_API_KEY</label>
              <input
                type="password"
                value={env.OPENAI_API_KEY ?? ''}
                onChange={(e) => setEnv(prev => ({ ...prev, OPENAI_API_KEY: e.target.value }))}
                placeholder="sk-..."
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-blue-500 outline-none transition"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">ANTHROPIC_API_KEY</label>
              <input
                type="password"
                value={env.ANTHROPIC_API_KEY ?? ''}
                onChange={(e) => setEnv(prev => ({ ...prev, ANTHROPIC_API_KEY: e.target.value }))}
                placeholder="sk-ant-..."
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-blue-500 outline-none transition"
              />
            </div>
          </div>
          <div className="mt-4 flex items-center gap-2">
            <button
              onClick={handleSaveEnv}
              disabled={envSaving}
              className="flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg font-medium transition disabled:opacity-50"
            >
              {envSaved ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
              {envSaving ? 'Saving...' : envSaved ? 'Saved!' : 'Save environment'}
            </button>
            <Link to="/app/env" className="flex items-center gap-2 text-sm text-blue-400 hover:text-blue-300">
              <ExternalLink className="w-4 h-4" /> Full env panel
            </Link>
          </div>
        </motion.div>
      )}

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
              <Link to="/pricing" className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 text-sm mt-2">
                <FileText className="w-4 h-4" /> Pricing plans
              </Link>
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

      {/* Save Button (profile / notifications) */}
      {(activeTab === 'profile' || activeTab === 'notifications') && (
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
      )}
      </div>
    </div>
  );
};

export default Settings;