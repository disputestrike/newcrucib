import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Zap, Bot, Layers, Shield, Rocket, Code, Database, Globe, ChevronRight, Play, ArrowRight, Check, Star, Menu, X } from 'lucide-react';
import { useAuth } from '../App';

const LandingPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const features = [
    { icon: Bot, title: '20 AI Agents', desc: 'Specialized agents for every task from planning to deployment' },
    { icon: Zap, title: '< 1 Hour Generation', desc: 'Full-stack apps generated 4x faster than competitors' },
    { icon: Layers, title: 'Multi-Format Export', desc: 'PDF, Excel, Markdown, and more with one click' },
    { icon: Shield, title: '95/100 Code Quality', desc: '5-layer validation ensures production-ready code' },
    { icon: Database, title: 'Memory System', desc: 'Learns from 10K+ projects for continuous improvement' },
    { icon: Globe, title: 'One-Click Deploy', desc: 'Railway, Vercel, AWS deployment built-in' }
  ];

  const pricing = [
    { name: 'Starter', price: 9.99, tokens: '100K', features: ['1-2 projects', 'Basic exports', 'Community support'] },
    { name: 'Pro', price: 49.99, tokens: '500K', features: ['5-10 projects', 'All export formats', 'Priority support'], popular: true },
    { name: 'Professional', price: 99.99, tokens: '1.2M', features: ['20+ projects', 'Advanced patterns', 'Team features'] },
    { name: 'Enterprise', price: 299.99, tokens: '5M', features: ['Unlimited projects', 'White-label', 'SLA guarantee'] }
  ];

  const agents = [
    { name: 'Planner', layer: 'Planning', color: 'blue' },
    { name: 'Frontend', layer: 'Execution', color: 'green' },
    { name: 'Backend', layer: 'Execution', color: 'green' },
    { name: 'Security', layer: 'Validation', color: 'purple' },
    { name: 'Deploy', layer: 'Deployment', color: 'orange' }
  ];

  return (
    <div className="min-h-screen bg-[#050505] text-white overflow-x-hidden">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Bot className="w-6 h-6" />
            </div>
            <span className="text-xl font-bold">AgentForge</span>
          </Link>
          
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-gray-400 hover:text-white transition">Features</a>
            <a href="#agents" className="text-gray-400 hover:text-white transition">Agents</a>
            <a href="#pricing" className="text-gray-400 hover:text-white transition">Pricing</a>
          </div>

          <div className="hidden md:flex items-center gap-4">
            {user ? (
              <button onClick={() => navigate('/app')} className="px-5 py-2.5 bg-blue-500 hover:bg-blue-600 rounded-lg font-medium transition neon-blue" data-testid="go-to-dashboard-btn">
                Dashboard
              </button>
            ) : (
              <>
                <button onClick={() => navigate('/auth')} className="px-5 py-2.5 text-gray-300 hover:text-white transition" data-testid="login-btn">
                  Log In
                </button>
                <button onClick={() => navigate('/auth?mode=register')} className="px-5 py-2.5 bg-blue-500 hover:bg-blue-600 rounded-lg font-medium transition neon-blue" data-testid="get-started-btn">
                  Get Started
                </button>
              </>
            )}
          </div>

          <button className="md:hidden" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </nav>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-40 bg-black/90 pt-20 px-6 md:hidden">
          <div className="flex flex-col gap-6">
            <a href="#features" className="text-xl" onClick={() => setMobileMenuOpen(false)}>Features</a>
            <a href="#agents" className="text-xl" onClick={() => setMobileMenuOpen(false)}>Agents</a>
            <a href="#pricing" className="text-xl" onClick={() => setMobileMenuOpen(false)}>Pricing</a>
            <button onClick={() => { navigate('/auth'); setMobileMenuOpen(false); }} className="w-full py-3 bg-blue-500 rounded-lg font-medium mt-4">
              Get Started
            </button>
          </div>
        </div>
      )}

      {/* Hero */}
      <section className="relative pt-32 pb-20 px-6">
        <div className="absolute inset-0 grid-pattern opacity-30"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-blue-500/20 rounded-full blur-[150px]"></div>
        
        <div className="max-w-7xl mx-auto relative">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center max-w-4xl mx-auto"
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500/10 border border-blue-500/30 rounded-full mb-8">
              <Zap className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-blue-400">Now with 20 specialized AI agents</span>
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              Build Full-Stack Apps in
              <span className="bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent"> Under 1 Hour</span>
            </h1>
            
            <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
              The most advanced AI agent orchestration platform. 20 specialized agents working in parallel to generate, validate, and deploy production-ready applications.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <button 
                onClick={() => navigate(user ? '/app/projects/new' : '/auth?mode=register')}
                className="group px-8 py-4 bg-blue-500 hover:bg-blue-600 rounded-lg font-medium text-lg transition-all neon-blue flex items-center gap-2"
                data-testid="hero-cta-btn"
              >
                Start Building Free
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
              <button className="px-8 py-4 border border-white/20 hover:border-white/40 rounded-lg font-medium text-lg transition flex items-center gap-2" data-testid="watch-demo-btn">
                <Play className="w-5 h-5" />
                Watch Demo
              </button>
            </div>
            
            <div className="flex items-center justify-center gap-8 mt-12 text-sm text-gray-500">
              <div className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-500" />
                50K free tokens
              </div>
              <div className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-500" />
                No credit card required
              </div>
              <div className="flex items-center gap-2">
                <Check className="w-4 h-4 text-green-500" />
                Deploy in minutes
              </div>
            </div>
          </motion.div>

          {/* Hero Visual */}
          <motion.div 
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-20 relative"
          >
            <div className="aspect-video max-w-5xl mx-auto bg-[#0a0a0a] rounded-2xl border border-white/10 overflow-hidden">
              <div className="h-10 bg-[#111] border-b border-white/10 flex items-center gap-2 px-4">
                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
                <span className="ml-4 text-xs text-gray-500 mono">AgentForge Dashboard</span>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-4 gap-4 mb-6">
                  {agents.map((agent, i) => (
                    <motion.div 
                      key={agent.name}
                      initial={{ opacity: 0, scale: 0.8 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: 0.5 + i * 0.1 }}
                      className={`p-4 rounded-lg border ${
                        agent.color === 'blue' ? 'bg-blue-500/10 border-blue-500/30' :
                        agent.color === 'green' ? 'bg-green-500/10 border-green-500/30' :
                        agent.color === 'purple' ? 'bg-purple-500/10 border-purple-500/30' :
                        'bg-orange-500/10 border-orange-500/30'
                      }`}
                    >
                      <Bot className={`w-6 h-6 mb-2 ${
                        agent.color === 'blue' ? 'text-blue-400' :
                        agent.color === 'green' ? 'text-green-400' :
                        agent.color === 'purple' ? 'text-purple-400' :
                        'text-orange-400'
                      }`} />
                      <p className="text-sm font-medium">{agent.name}</p>
                      <p className="text-xs text-gray-500">{agent.layer}</p>
                    </motion.div>
                  ))}
                </div>
                <div className="h-32 bg-[#080808] rounded-lg border border-white/5 flex items-center justify-center">
                  <div className="flex items-center gap-4">
                    <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-gray-400">Generating your application...</span>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Everything You Need to Ship Faster</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">Our 20-agent system handles everything from planning to deployment, so you can focus on what matters.</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="group p-6 bg-[#0a0a0a] rounded-xl border border-white/5 hover:border-blue-500/30 transition-colors"
              >
                <div className="w-12 h-12 bg-blue-500/10 rounded-lg flex items-center justify-center mb-4 group-hover:bg-blue-500/20 transition">
                  <feature.icon className="w-6 h-6 text-blue-400" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Agent Layers */}
      <section id="agents" className="py-20 px-6 bg-[#080808]">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">4-Layer Agent Architecture</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">Each layer specializes in different aspects of app generation, working in parallel for maximum efficiency.</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { layer: 'Planning', agents: ['Planner', 'Requirements', 'Stack Selector'], color: 'blue', icon: Layers },
              { layer: 'Execution', agents: ['Frontend', 'Backend', 'Database', 'Tests'], color: 'green', icon: Code },
              { layer: 'Validation', agents: ['Security', 'QA', 'Performance'], color: 'purple', icon: Shield },
              { layer: 'Deployment', agents: ['Deploy', 'Error Recovery', 'Memory'], color: 'orange', icon: Rocket }
            ].map((section, i) => (
              <motion.div
                key={section.layer}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15 }}
                className={`p-6 rounded-xl border ${
                  section.color === 'blue' ? 'bg-blue-500/5 border-blue-500/20' :
                  section.color === 'green' ? 'bg-green-500/5 border-green-500/20' :
                  section.color === 'purple' ? 'bg-purple-500/5 border-purple-500/20' :
                  'bg-orange-500/5 border-orange-500/20'
                }`}
              >
                <section.icon className={`w-8 h-8 mb-4 ${
                  section.color === 'blue' ? 'text-blue-400' :
                  section.color === 'green' ? 'text-green-400' :
                  section.color === 'purple' ? 'text-purple-400' :
                  'text-orange-400'
                }`} />
                <h3 className="text-xl font-semibold mb-4">{section.layer}</h3>
                <ul className="space-y-2">
                  {section.agents.map(agent => (
                    <li key={agent} className="flex items-center gap-2 text-gray-400">
                      <div className={`w-2 h-2 rounded-full ${
                        section.color === 'blue' ? 'bg-blue-400' :
                        section.color === 'green' ? 'bg-green-400' :
                        section.color === 'purple' ? 'bg-purple-400' :
                        'bg-orange-400'
                      }`}></div>
                      {agent}
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Simple Token-Based Pricing</h2>
            <p className="text-gray-400 max-w-2xl mx-auto">Pay for what you use. No subscriptions, no hidden fees. Unused tokens never expire.</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {pricing.map((plan, i) => (
              <motion.div
                key={plan.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className={`relative p-6 rounded-xl border transition-all ${
                  plan.popular 
                    ? 'bg-blue-500/10 border-blue-500/50 scale-105' 
                    : 'bg-[#0a0a0a] border-white/10 hover:border-white/20'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-blue-500 rounded-full text-xs font-medium">
                    Most Popular
                  </div>
                )}
                <h3 className="text-xl font-semibold mb-2">{plan.name}</h3>
                <div className="mb-4">
                  <span className="text-4xl font-bold">${plan.price}</span>
                  <span className="text-gray-500"> / {plan.tokens} tokens</span>
                </div>
                <ul className="space-y-3 mb-6">
                  {plan.features.map(feature => (
                    <li key={feature} className="flex items-center gap-2 text-gray-400">
                      <Check className="w-4 h-4 text-green-500" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <button 
                  onClick={() => navigate(user ? '/app/tokens' : '/auth?mode=register')}
                  className={`w-full py-3 rounded-lg font-medium transition ${
                    plan.popular 
                      ? 'bg-blue-500 hover:bg-blue-600 neon-blue' 
                      : 'bg-white/10 hover:bg-white/20'
                  }`}
                  data-testid={`pricing-${plan.name.toLowerCase()}-btn`}
                >
                  Get Started
                </button>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="p-12 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-2xl border border-white/10"
          >
            <h2 className="text-4xl font-bold mb-4">Ready to Build Something Amazing?</h2>
            <p className="text-gray-400 mb-8">Join thousands of developers who are shipping faster with AgentForge.</p>
            <button 
              onClick={() => navigate(user ? '/app/projects/new' : '/auth?mode=register')}
              className="px-8 py-4 bg-blue-500 hover:bg-blue-600 rounded-lg font-medium text-lg transition neon-blue"
              data-testid="final-cta-btn"
            >
              Start Building Free
            </button>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-white/10">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Bot className="w-5 h-5" />
              </div>
              <span className="font-bold">AgentForge</span>
            </div>
            <p className="text-gray-500 text-sm">© 2026 AgentForge. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;