import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Zap, Check, ArrowRight } from 'lucide-react';
import { useAuth, API } from '../App';
import PublicNav from '../components/PublicNav';
import PublicFooter from '../components/PublicFooter';
import axios from 'axios';

const DEFAULT_BUNDLES = {
  starter: { tokens: 100000, price: 9.99 },
  pro: { tokens: 500000, price: 49.99 },
  professional: { tokens: 1200000, price: 99.99 },
  enterprise: { tokens: 5000000, price: 299.99 },
  unlimited: { tokens: 25000000, price: 999.99 }
};

const BUNDLE_ORDER = ['starter', 'pro', 'professional', 'enterprise', 'unlimited'];
const BUNDLE_LABELS = {
  starter: 'Starter',
  pro: 'Pro',
  professional: 'Professional',
  enterprise: 'Enterprise',
  unlimited: 'Unlimited'
};

export default function Pricing() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [bundles, setBundles] = useState(DEFAULT_BUNDLES);

  useEffect(() => {
    axios.get(`${API}/tokens/bundles`, { timeout: 5000 })
      .then((r) => {
        if (r.data?.bundles && Object.keys(r.data.bundles).length > 0) {
          setBundles(r.data.bundles);
        }
      })
      .catch(() => {});
  }, []);

  const formatTokens = (n) => {
    if (n >= 1e6) return `${(n / 1e6).toFixed(1)}M`;
    if (n >= 1e3) return `${(n / 1e3).toFixed(0)}K`;
    return String(n);
  };

  return (
    <div className="min-h-screen bg-kimi-bg text-kimi-text grid-pattern-kimi">
      <PublicNav />
      <div className="max-w-6xl mx-auto px-6 py-16">
        <div className="text-center mb-16">
          <span className="text-xs uppercase tracking-wider text-kimi-muted">Plans</span>
          <h1 className="text-kimi-section font-bold text-kimi-text mt-2 mb-4">Pricing</h1>
          <p className="text-kimi-muted max-w-xl mx-auto">Token-based plans. Free tier includes credits. Pay for what you use. No expiry—your tokens stay until you use them.</p>
        </div>

        {/* Free tier */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12 p-8 rounded-2xl border border-zinc-800 bg-zinc-900/30 max-w-2xl mx-auto"
        >
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
            <div>
              <h2 className="text-2xl font-semibold mb-2">Start for free</h2>
              <p className="text-zinc-500 mb-4">Try CrucibAI with no credit card. Build, export, and deploy.</p>
              <ul className="space-y-2 text-sm text-zinc-400">
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-green-500 shrink-0" /> Core build & preview</li>
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-green-500 shrink-0" /> Export to ZIP & GitHub</li>
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-green-500 shrink-0" /> All 20 AI agents</li>
                <li className="flex items-center gap-2"><Check className="w-4 h-4 text-green-500 shrink-0" /> Templates & prompt library</li>
              </ul>
            </div>
            <div className="shrink-0">
              <p className="text-3xl font-bold mb-2">$0</p>
              <p className="text-zinc-500 text-sm mb-4">No credit card required</p>
              <button
                onClick={() => navigate(user ? '/app' : '/auth?mode=register')}
                className="w-full md:w-auto px-6 py-3 bg-white text-black font-medium rounded-lg hover:bg-zinc-200 transition"
              >
                {user ? 'Go to Workspace' : 'Get started free'}
              </button>
            </div>
          </div>
        </motion.div>

        {/* Token bundles */}
        <h2 className="text-xl font-semibold text-center mb-2">Token packs</h2>
        <p className="text-zinc-500 text-center mb-10">Buy tokens once. Use them for builds. They don’t expire.</p>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
          {BUNDLE_ORDER.filter((k) => bundles[k]).map((key, i) => {
            const b = bundles[key];
            const isPro = key === 'pro';
            return (
              <motion.div
                key={key}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className={`relative p-6 rounded-2xl border ${
                  isPro ? 'border-blue-500/50 bg-blue-500/5' : 'border-zinc-800 bg-zinc-900/30'
                }`}
              >
                {isPro && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full bg-blue-500 text-white text-xs font-medium">
                    Popular
                  </span>
                )}
                <div className="flex items-center gap-2 mb-4">
                  <Zap className="w-5 h-5 text-yellow-500" />
                  <h3 className="text-lg font-semibold">{BUNDLE_LABELS[key]}</h3>
                </div>
                <div className="mb-2">
                  <span className="text-3xl font-bold">${Number(b.price).toFixed(2)}</span>
                </div>
                <p className="text-zinc-500 text-sm mb-6">
                  {formatTokens(b.tokens)} tokens
                </p>
                <ul className="space-y-2 text-xs text-zinc-400 mb-6">
                  <li className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-green-500 shrink-0" /> All features</li>
                  <li className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-green-500 shrink-0" /> No expiry</li>
                  <li className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-green-500 shrink-0" /> Priority support {key === 'enterprise' || key === 'unlimited' ? '✓' : ''}</li>
                </ul>
                <button
                  onClick={() => navigate(user ? '/app/tokens' : '/auth?mode=register')}
                  className={`w-full py-2.5 rounded-lg font-medium transition flex items-center justify-center gap-2 ${
                    isPro ? 'bg-blue-500 hover:bg-blue-600' : 'bg-zinc-700 hover:bg-zinc-600'
                  }`}
                >
                  {user ? 'Buy tokens' : 'Get started'}
                  <ArrowRight className="w-4 h-4" />
                </button>
              </motion.div>
            );
          })}
        </div>

        <p className="text-center text-zinc-500 text-sm mt-10">
          Need a custom plan? <a href="mailto:support@crucibai.com" className="text-blue-400 hover:text-blue-300">Contact us</a>.
        </p>

        {/* FAQ snippet */}
        <div className="mt-20 max-w-2xl mx-auto border-t border-zinc-800 pt-16">
          <h3 className="text-lg font-semibold mb-4">How tokens work</h3>
          <p className="text-zinc-500 text-sm leading-relaxed">
            Each AI build (and modification) uses tokens. One prompt might use a few hundred to a few thousand tokens depending on model and response length. Your balance is shown in the app; when you run low, buy another pack. Unused tokens never expire.
          </p>
        </div>
      </div>
      <PublicFooter />
    </div>
  );
}
