import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Send, Loader2, Sparkles, Play, ArrowRight, Check, Menu, X, Code, Layers, Zap, Globe, Shield, Database } from 'lucide-react';
import { useAuth, API } from '../App';
import axios from 'axios';

const LandingPage = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [openFaq, setOpenFaq] = useState(null);
  
  // Chat state
  const [chatInput, setChatInput] = useState('');
  const [chatMessages, setMessages] = useState([
    { role: 'assistant', content: "Hi! I'm CrucibAI. Describe what you want to build and I'll create it for you instantly." }
  ]);
  const [chatLoading, setChatLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  const generateCode = async () => {
    if (!prompt.trim()) return;
    navigate('/builder', { state: { prompt: prompt } });
  };

  const handleSendMessage = async (e) => {
    e?.preventDefault();
    if (!chatInput.trim() || chatLoading) return;

    const userMessage = chatInput.trim();
    
    // If it's a substantial prompt, redirect to builder
    if (userMessage.length > 20 && (userMessage.toLowerCase().includes('build') || userMessage.toLowerCase().includes('create') || userMessage.toLowerCase().includes('make'))) {
      navigate('/builder', { state: { prompt: userMessage } });
      return;
    }

    setChatInput('');
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setChatLoading(true);

    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const res = await axios.post(`${API}/ai/chat`, {
        message: userMessage,
        session_id: sessionId,
        model: 'auto'
      }, { headers });

      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: res.data.response,
        model: res.data.model_used
      }]);
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: "Sorry, I encountered an error. Please try again.",
        error: true
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  const features = [
    { icon: Code, title: 'Build websites and mobile apps', desc: 'Transform your ideas into fully functional websites and mobile apps with instant deployment, seamless data connections, and powerful scalability.' },
    { icon: Sparkles, title: 'Build custom agents', desc: 'Create specialized AI agents tailored to your specific use case and workflow requirements.' },
    { icon: Layers, title: 'Build powerful integrations', desc: 'Connect with any API, database, or third-party service seamlessly.' }
  ];

  const faqs = [
    { q: 'What is CrucibAI and how does it work?', a: 'CrucibAI is an AI-powered development platform that transforms your ideas into fully functional applications. Simply describe what you want to build in natural language, and our AI handles the coding, design, and deployment. No programming experience required.' },
    { q: 'What can I build with CrucibAI?', a: 'You can build websites, web applications, mobile apps, APIs, automation workflows, dashboards, and much more. Our platform supports React, Node.js, Python, and integrates with popular services like Stripe, OpenAI, and databases.' },
    { q: "How does CrucibAI's pricing work?", a: 'We use a token-based pricing system. You purchase tokens and use them as you build. Start free with 50,000 tokens. Unused tokens never expire. Plans range from $9.99 (100K tokens) to $299.99 (5M tokens).' },
    { q: 'Do I need coding experience to use CrucibAI?', a: 'No! CrucibAI is designed for everyone. Just describe what you want in plain English, and our AI agents will handle the technical implementation. Of course, developers can also dive into the code if they want more control.' }
  ];

  const pricing = [
    { name: 'Free', icon: '🎁', desc: 'Get started with essential features at no cost', price: 0, features: ['50,000 free tokens', 'Access to all AI models', 'Basic exports', 'Community support'] },
    { name: 'Standard', icon: '⚡', desc: 'Perfect for first-time builders', price: 17, save: 36, features: ['Everything in Free, plus:', '100,000 tokens/month', 'Priority support', 'All export formats'] },
    { name: 'Pro', icon: '✨', desc: 'Built for serious creators and brands', price: 167, save: 396, features: ['Everything in Standard, plus:', '1M context window', 'Custom AI agents', 'Team collaboration', 'API access'] }
  ];

  return (
    <div className="min-h-screen bg-white text-gray-900">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <span className="text-2xl font-bold tracking-tight">crucib<span className="text-blue-600">ai</span></span>
          </Link>
          
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-gray-600 hover:text-gray-900 transition font-medium">Features</a>
            <a href="#pricing" className="text-gray-600 hover:text-gray-900 transition font-medium">Pricing</a>
            <a href="#faq" className="text-gray-600 hover:text-gray-900 transition font-medium">FAQs</a>
          </div>

          <div className="hidden md:flex items-center gap-4">
            {user ? (
              <button onClick={() => navigate('/app')} className="px-5 py-2.5 bg-gray-900 hover:bg-gray-800 text-white rounded-full font-medium transition flex items-center gap-2" data-testid="go-to-dashboard-btn">
                Dashboard <ArrowRight className="w-4 h-4" />
              </button>
            ) : (
              <>
                <button onClick={() => navigate('/auth')} className="px-5 py-2.5 text-gray-600 hover:text-gray-900 transition font-medium" data-testid="login-btn">
                  Sign in
                </button>
                <button onClick={() => navigate('/auth?mode=register')} className="px-5 py-2.5 bg-gray-900 hover:bg-gray-800 text-white rounded-full font-medium transition flex items-center gap-2" data-testid="get-started-btn">
                  Get Started <ArrowRight className="w-4 h-4" />
                </button>
              </>
            )}
          </div>

          <button className="md:hidden p-2" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="fixed inset-0 z-40 bg-white pt-20 px-6 md:hidden"
          >
            <div className="flex flex-col gap-6">
              <a href="#features" className="text-xl font-medium" onClick={() => setMobileMenuOpen(false)}>Features</a>
              <a href="#pricing" className="text-xl font-medium" onClick={() => setMobileMenuOpen(false)}>Pricing</a>
              <a href="#faq" className="text-xl font-medium" onClick={() => setMobileMenuOpen(false)}>FAQs</a>
              <button onClick={() => { navigate('/auth'); setMobileMenuOpen(false); }} className="w-full py-3 bg-gray-900 text-white rounded-full font-medium mt-4">
                Get Started
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Hero */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center max-w-4xl mx-auto mb-16"
          >
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight tracking-tight">
              Build production-ready apps through conversation
            </h1>
            
            <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
              Chat with AI agents that design, code, and deploy your application from start to finish. No programming experience required.
            </p>
          </motion.div>

          {/* Chat Interface */}
          <motion.div 
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="max-w-3xl mx-auto"
          >
            <div className="bg-white rounded-2xl border border-gray-200 shadow-2xl shadow-gray-200/50 overflow-hidden">
              {/* Chat Header */}
              <div className="px-6 py-4 border-b border-gray-100 flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-red-400"></div>
                <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                <div className="w-3 h-3 rounded-full bg-green-400"></div>
                <span className="ml-4 text-sm text-gray-500 font-medium">CrucibAI Chat</span>
              </div>
              
              {/* Chat Messages */}
              <div className="h-80 overflow-y-auto p-6 space-y-4 bg-gray-50/50" data-testid="landing-chat-messages">
                {chatMessages.map((msg, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div className={`max-w-[85%] p-4 rounded-2xl ${
                      msg.role === 'user' 
                        ? 'bg-gray-900 text-white' 
                        : msg.error 
                          ? 'bg-red-50 border border-red-200 text-red-700'
                          : 'bg-white border border-gray-200 text-gray-800 shadow-sm'
                    }`}>
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                      {msg.model && (
                        <p className="text-xs text-gray-400 mt-2 flex items-center gap-1">
                          <Sparkles className="w-3 h-3" />
                          {msg.model}
                        </p>
                      )}
                    </div>
                  </motion.div>
                ))}
                {chatLoading && (
                  <div className="flex justify-start">
                    <div className="bg-white border border-gray-200 p-4 rounded-2xl shadow-sm">
                      <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                    </div>
                  </div>
                )}
                <div ref={chatEndRef} />
              </div>
              
              {/* Chat Input */}
              <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-100 bg-white">
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={chatInput}
                    onChange={(e) => setChatInput(e.target.value)}
                    placeholder="Describe what you want to build..."
                    className="flex-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition text-sm"
                    data-testid="landing-chat-input"
                  />
                  <button
                    type="submit"
                    disabled={chatLoading || !chatInput.trim()}
                    className="px-5 py-3 bg-gray-900 hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-xl transition flex items-center gap-2 font-medium"
                    data-testid="landing-chat-send"
                  >
                    {chatLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
                  </button>
                </div>
              </form>
            </div>
            
            <p className="text-center text-sm text-gray-500 mt-4">
              Free to try • No sign-up required • Powered by GPT-4o, Claude & Gemini
            </p>
          </motion.div>
        </div>
      </section>

      {/* What can CrucibAI do */}
      <section id="features" className="py-24 px-6 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">What can CrucibAI do for you?</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              From concept to deployment, CrucibAI handles every aspect of software development so you can focus on what matters most - your vision!
            </p>
          </div>
          
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="space-y-8">
              {features.map((feature, i) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, x: -20 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  className="flex gap-4"
                >
                  <div className="flex-shrink-0 w-12 h-12 bg-gray-900 rounded-xl flex items-center justify-center">
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                    <p className="text-gray-600 leading-relaxed">{feature.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>
            
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="relative"
            >
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 rounded-3xl p-8 shadow-2xl">
                <div className="bg-white rounded-2xl overflow-hidden shadow-lg">
                  <div className="h-8 bg-gray-100 flex items-center gap-2 px-4">
                    <div className="w-2.5 h-2.5 rounded-full bg-red-400"></div>
                    <div className="w-2.5 h-2.5 rounded-full bg-yellow-400"></div>
                    <div className="w-2.5 h-2.5 rounded-full bg-green-400"></div>
                  </div>
                  <div className="p-4 bg-gray-50">
                    <div className="space-y-3">
                      <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                      <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                      <div className="h-20 bg-blue-100 rounded-lg mt-4"></div>
                      <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                      <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                    </div>
                  </div>
                </div>
                <div className="absolute -bottom-4 -right-4 bg-white rounded-xl p-4 shadow-xl border border-gray-100">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                      <Check className="w-5 h-5 text-green-600" />
                    </div>
                    <div>
                      <p className="font-semibold text-sm">Deployed!</p>
                      <p className="text-xs text-gray-500">app.crucibai.dev</p>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Video Section */}
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-4">PRODUCT VIDEO</p>
          <h2 className="text-4xl md:text-5xl font-bold mb-12 tracking-tight">See CrucibAI in Action</h2>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="relative max-w-4xl mx-auto rounded-2xl overflow-hidden bg-gradient-to-br from-gray-900 to-gray-800 aspect-video flex items-center justify-center cursor-pointer group"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-blue-600/20 to-purple-600/20"></div>
            <button className="relative z-10 w-20 h-20 bg-white rounded-full flex items-center justify-center shadow-2xl group-hover:scale-110 transition-transform">
              <Play className="w-8 h-8 text-gray-900 ml-1" />
            </button>
            <p className="absolute bottom-8 left-1/2 -translate-x-1/2 text-white/80 text-sm">Watch how developers build apps in minutes</p>
          </motion.div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 px-6 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4 tracking-tight">Transparent pricing for every builder</h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Choose the plan that fits your building ambitions. From weekend projects to enterprise applications, we've got you covered.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {pricing.map((plan, i) => (
              <motion.div
                key={plan.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className={`p-8 rounded-2xl border ${
                  plan.name === 'Pro' 
                    ? 'bg-white border-blue-200 shadow-xl shadow-blue-100/50 scale-105' 
                    : 'bg-white border-gray-200'
                }`}
              >
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-2xl">{plan.icon}</span>
                  <h3 className="text-xl font-bold">{plan.name}</h3>
                </div>
                <p className="text-gray-600 text-sm mb-6">{plan.desc}</p>
                
                <div className="mb-6">
                  <span className="text-4xl font-bold">${plan.price}</span>
                  <span className="text-gray-500">/ month</span>
                  {plan.save && (
                    <span className="ml-2 text-sm text-green-600 font-medium">Save ${plan.save}</span>
                  )}
                </div>
                
                <ul className="space-y-3 mb-8">
                  {plan.features.map(feature => (
                    <li key={feature} className="flex items-start gap-2 text-sm">
                      <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <button 
                  onClick={() => navigate(user ? '/app/tokens' : '/auth?mode=register')}
                  className={`w-full py-3 rounded-xl font-medium transition ${
                    plan.name === 'Pro' 
                      ? 'bg-gray-900 hover:bg-gray-800 text-white' 
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-900'
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

      {/* FAQ */}
      <section id="faq" className="py-24 px-6">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-16">
            <p className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-4">FREQUENTLY ASKED QUESTIONS</p>
            <h2 className="text-4xl md:text-5xl font-bold tracking-tight">Curious about CrucibAI?<br />We got you covered</h2>
          </div>
          
          <div className="space-y-4">
            {faqs.map((faq, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="border-b border-gray-200"
              >
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full py-6 flex items-center justify-between text-left"
                  data-testid={`faq-${i}`}
                >
                  <span className="text-lg font-semibold pr-8">{faq.q}</span>
                  <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${openFaq === i ? 'rotate-180' : ''}`} />
                </button>
                <AnimatePresence>
                  {openFaq === i && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <p className="pb-6 text-gray-600 leading-relaxed">{faq.a}</p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6 bg-gray-900 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 tracking-tight">Ready to build something amazing?</h2>
          <p className="text-xl text-gray-400 mb-10">Join thousands of developers shipping faster with CrucibAI.</p>
          <button 
            onClick={() => navigate(user ? '/app/projects/new' : '/auth?mode=register')}
            className="px-8 py-4 bg-white hover:bg-gray-100 text-gray-900 rounded-full font-medium text-lg transition flex items-center gap-2 mx-auto"
            data-testid="final-cta-btn"
          >
            Start Building Free <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-16 px-6 bg-white border-t border-gray-100">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-5 gap-12 mb-12">
            <div className="md:col-span-2">
              <span className="text-2xl font-bold tracking-tight">crucib<span className="text-blue-600">ai</span></span>
              <p className="text-gray-600 mt-4 max-w-sm">
                Build production-ready apps through conversation. Chat with AI agents that design, code, and deploy your application from start to finish.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-3 text-gray-600">
                <li><a href="#" className="hover:text-gray-900 transition">Build</a></li>
                <li><a href="#pricing" className="hover:text-gray-900 transition">Pricing</a></li>
                <li><a href="#" className="hover:text-gray-900 transition">Integrations</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Solutions</h4>
              <ul className="space-y-3 text-gray-600">
                <li><a href="#" className="hover:text-gray-900 transition">Enterprise</a></li>
                <li><a href="#" className="hover:text-gray-900 transition">SMB Owners</a></li>
                <li><a href="#" className="hover:text-gray-900 transition">IT Agencies</a></li>
                <li><a href="#" className="hover:text-gray-900 transition">Product Managers</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-3 text-gray-600">
                <li><a href="#" className="hover:text-gray-900 transition">About</a></li>
                <li><a href="#" className="hover:text-gray-900 transition">Careers</a></li>
                <li><a href="#" className="hover:text-gray-900 transition">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-gray-900 transition">Terms of Service</a></li>
              </ul>
            </div>
          </div>
          
          <div className="pt-8 border-t border-gray-100 flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-gray-500 text-sm">© 2026 CrucibAI. All rights reserved.</p>
            <p className="text-gray-400 text-sm">Designed and built with 💙 by CrucibAI</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
