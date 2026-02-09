import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Send, Loader2, ArrowRight, Check, Menu, X, Play, ArrowUpRight } from 'lucide-react';
import { useAuth, API } from '../App';
import axios from 'axios';

const LandingPage = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [openFaq, setOpenFaq] = useState(null);
  
  // Build state
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isBuilding, setIsBuilding] = useState(false);
  const [buildProgress, setBuildProgress] = useState(0);
  const [generatedCode, setGeneratedCode] = useState(null);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const startBuild = async (prompt) => {
    if (!prompt.trim() || isBuilding) return;

    const userPrompt = prompt.trim();
    setInput('');
    setIsBuilding(true);
    setBuildProgress(0);
    setMessages(prev => [...prev, { role: 'user', content: userPrompt }]);

    setMessages(prev => [...prev, { 
      role: 'assistant', 
      content: 'Working on it...',
      isBuilding: true
    }]);

    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const progressInterval = setInterval(() => {
        setBuildProgress(prev => Math.min(prev + Math.random() * 15, 90));
      }, 500);

      const response = await axios.post(`${API}/ai/chat`, {
        message: `Create a complete, production-ready React application for: "${userPrompt}". Use React hooks and Tailwind CSS. Make it modern and functional. Respond with ONLY the code.`,
        session_id: sessionId,
        model: 'auto'
      }, { headers, timeout: 60000 });

      clearInterval(progressInterval);
      setBuildProgress(100);

      const code = response.data.response.replace(/```jsx?/g, '').replace(/```/g, '').trim();

      setGeneratedCode({ name: userPrompt.slice(0, 30), code });

      setMessages(prev => prev.map((msg, i) => 
        i === prev.length - 1 
          ? { role: 'assistant', content: `Done. Your app is ready below. Tell me what to change.`, hasCode: true }
          : msg
      ));

    } catch (error) {
      setMessages(prev => prev.map((msg, i) => 
        i === prev.length - 1 
          ? { role: 'assistant', content: `Something went wrong. Try again.`, error: true }
          : msg
      ));
    } finally {
      setIsBuilding(false);
    }
  };

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!input.trim()) return;
    
    if (generatedCode) {
      modifyCode(input);
    } else {
      startBuild(input);
    }
  };

  const modifyCode = async (request) => {
    if (!request.trim() || isBuilding) return;

    setInput('');
    setIsBuilding(true);
    setMessages(prev => [...prev, { role: 'user', content: request }]);
    setMessages(prev => [...prev, { role: 'assistant', content: 'Updating...', isBuilding: true }]);

    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const response = await axios.post(`${API}/ai/chat`, {
        message: `Current code:\n\n${generatedCode.code}\n\nModify it to: "${request}"\n\nRespond with ONLY the complete updated code.`,
        session_id: sessionId,
        model: 'auto'
      }, { headers, timeout: 60000 });

      const newCode = response.data.response.replace(/```jsx?/g, '').replace(/```/g, '').trim();

      if (newCode.includes('import') || newCode.includes('function') || newCode.includes('const')) {
        setGeneratedCode(prev => ({ ...prev, code: newCode }));
        setMessages(prev => prev.map((msg, i) => 
          i === prev.length - 1 ? { role: 'assistant', content: `Updated. What else?`, hasCode: true } : msg
        ));
      } else {
        setMessages(prev => prev.map((msg, i) => 
          i === prev.length - 1 ? { role: 'assistant', content: response.data.response } : msg
        ));
      }
    } catch (error) {
      setMessages(prev => prev.map((msg, i) => 
        i === prev.length - 1 ? { role: 'assistant', content: 'Error. Try again.', error: true } : msg
      ));
    } finally {
      setIsBuilding(false);
    }
  };

  const downloadCode = () => {
    if (!generatedCode) return;
    const blob = new Blob([generatedCode.code], { type: 'text/javascript' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'app.jsx';
    a.click();
  };

  const faqs = [
    { q: 'What is CrucibAI?', a: 'CrucibAI turns your ideas into working applications. Describe what you need, and we build it.' },
    { q: 'Do I need to code?', a: 'No. Just describe what you want in plain language.' },
    { q: 'What can I create?', a: 'Websites, apps, dashboards, tools — anything you can describe.' },
    { q: 'How do I make changes?', a: 'Just ask. Say "make it dark mode" or "add a sidebar" and we update it.' }
  ];

  return (
    <div className="min-h-screen bg-[#0A0A0B] text-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-5 flex items-center justify-between">
          <Link to="/" className="text-xl font-semibold tracking-tight">
            CrucibAI
          </Link>
          
          <div className="hidden md:flex items-center gap-8">
            <a href="#how" className="text-sm text-zinc-400 hover:text-white transition">How it works</a>
            <a href="#faq" className="text-sm text-zinc-400 hover:text-white transition">FAQ</a>
            {user ? (
              <button onClick={() => navigate('/app')} className="text-sm text-zinc-400 hover:text-white transition">
                Dashboard
              </button>
            ) : (
              <button onClick={() => navigate('/auth')} className="text-sm text-zinc-400 hover:text-white transition">
                Sign in
              </button>
            )}
            <button 
              onClick={() => navigate(user ? '/app' : '/auth?mode=register')} 
              className="px-4 py-2 bg-white text-black text-sm font-medium rounded-lg hover:bg-zinc-200 transition"
            >
              Get started
            </button>
          </div>

          <button className="md:hidden" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-[#0A0A0B] pt-20 px-6 md:hidden"
          >
            <div className="flex flex-col gap-6">
              <a href="#how" className="text-lg" onClick={() => setMobileMenuOpen(false)}>How it works</a>
              <a href="#faq" className="text-lg" onClick={() => setMobileMenuOpen(false)}>FAQ</a>
              <button onClick={() => { navigate('/auth'); setMobileMenuOpen(false); }} className="w-full py-3 bg-white text-black rounded-lg font-medium mt-4">
                Get started
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Hero */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-3xl mx-auto text-center">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl md:text-6xl font-semibold tracking-tight leading-[1.1] mb-6"
          >
            Turn your ideas into
            <br />
            <span className="text-zinc-500">working software</span>
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-lg text-zinc-500 mb-12 max-w-xl mx-auto"
          >
            Describe what you want to build. We handle the rest.
          </motion.p>
        </div>

        {/* Main Input */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="max-w-2xl mx-auto"
        >
          <div className="bg-[#141415] rounded-2xl overflow-hidden">
            {/* Messages */}
            {messages.length > 0 && (
              <div className="max-h-80 overflow-y-auto p-5 space-y-4">
                {messages.map((msg, i) => (
                  <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] px-4 py-3 rounded-xl text-sm ${
                      msg.role === 'user' 
                        ? 'bg-white text-black' 
                        : msg.error 
                          ? 'bg-red-500/10 text-red-400'
                          : 'bg-zinc-800 text-zinc-200'
                    }`}>
                      {msg.isBuilding ? (
                        <div className="flex items-center gap-2">
                          <div className="w-4 h-4 border-2 border-zinc-500 border-t-white rounded-full animate-spin" />
                          <span>{msg.content}</span>
                        </div>
                      ) : (
                        <span>{msg.content}</span>
                      )}
                    </div>
                  </div>
                ))}
                <div ref={chatEndRef} />
              </div>
            )}

            {/* Progress */}
            {isBuilding && (
              <div className="px-5 pb-2">
                <div className="h-0.5 bg-zinc-800 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-full bg-white"
                    initial={{ width: 0 }}
                    animate={{ width: `${buildProgress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Generated Code */}
            {generatedCode && !isBuilding && (
              <div className="px-5 pb-4">
                <div className="bg-[#0A0A0B] rounded-lg overflow-hidden">
                  <div className="flex items-center justify-between px-4 py-2 border-b border-zinc-800">
                    <span className="text-xs text-zinc-500 font-mono">app.jsx</span>
                    <button onClick={downloadCode} className="text-xs text-zinc-500 hover:text-white transition">
                      Download
                    </button>
                  </div>
                  <pre className="p-4 text-xs text-zinc-400 font-mono overflow-x-auto max-h-48 overflow-y-auto">
                    <code>{generatedCode.code.slice(0, 800)}{generatedCode.code.length > 800 ? '\n...' : ''}</code>
                  </pre>
                </div>
              </div>
            )}

            {/* Input */}
            <form onSubmit={handleSubmit} className="p-4">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={messages.length > 0 ? "Ask for changes..." : "What do you want to build?"}
                  className="flex-1 px-4 py-3 bg-[#1C1C1E] text-white placeholder-zinc-600 rounded-xl text-sm outline-none focus:ring-1 focus:ring-zinc-700 transition"
                  disabled={isBuilding}
                />
                <button
                  type="submit"
                  disabled={!input.trim() || isBuilding}
                  className="px-5 py-3 bg-white text-black rounded-xl text-sm font-medium disabled:opacity-30 disabled:cursor-not-allowed hover:bg-zinc-200 transition"
                >
                  {isBuilding ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <ArrowRight className="w-4 h-4" />
                  )}
                </button>
              </div>
              
              {messages.length === 0 && (
                <div className="flex flex-wrap gap-2 mt-4">
                  {['A task manager', 'Portfolio site', 'Pricing page', 'Dashboard'].map(s => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => setInput(s)}
                      className="px-3 py-1.5 text-xs text-zinc-500 bg-zinc-800/50 rounded-lg hover:bg-zinc-800 hover:text-zinc-300 transition"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </form>
          </div>
        </motion.div>
      </section>

      {/* How it works */}
      <section id="how" className="py-24 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-semibold text-center mb-16">How it works</h2>
          
          <div className="grid md:grid-cols-3 gap-12">
            {[
              { step: '01', title: 'Describe', desc: 'Tell us what you want in plain language. No technical jargon needed.' },
              { step: '02', title: 'Build', desc: 'We generate production-ready code in seconds. React, Tailwind, everything modern.' },
              { step: '03', title: 'Iterate', desc: 'Want changes? Just ask. We update the code instantly.' }
            ].map((item, i) => (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
              >
                <div className="text-xs text-zinc-600 font-mono mb-3">{item.step}</div>
                <h3 className="text-lg font-medium mb-2">{item.title}</h3>
                <p className="text-sm text-zinc-500 leading-relaxed">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Product Preview */}
      <section className="py-24 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="relative rounded-2xl overflow-hidden bg-gradient-to-b from-zinc-800/50 to-transparent p-px">
            <div className="bg-[#0A0A0B] rounded-2xl p-8 md:p-16">
              <div className="aspect-video bg-[#141415] rounded-xl flex items-center justify-center">
                <button className="w-16 h-16 bg-white/10 hover:bg-white/20 rounded-full flex items-center justify-center transition">
                  <Play className="w-6 h-6 text-white ml-1" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="py-24 px-6">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-2xl font-semibold text-center mb-12">Questions</h2>
          
          <div className="space-y-2">
            {faqs.map((faq, i) => (
              <div key={i} className="border-b border-zinc-800/50">
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full py-5 flex items-center justify-between text-left"
                >
                  <span className="text-sm font-medium">{faq.q}</span>
                  <ChevronDown className={`w-4 h-4 text-zinc-500 transition-transform ${openFaq === i ? 'rotate-180' : ''}`} />
                </button>
                <AnimatePresence>
                  {openFaq === i && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <p className="pb-5 text-sm text-zinc-500">{faq.a}</p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-24 px-6">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-semibold mb-4">Ready to build?</h2>
          <p className="text-zinc-500 mb-8">Start creating in seconds. No credit card required.</p>
          <button 
            onClick={() => navigate(user ? '/app' : '/auth?mode=register')}
            className="px-6 py-3 bg-white text-black font-medium rounded-lg hover:bg-zinc-200 transition"
          >
            Get started free
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-zinc-800/50">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-4 gap-12 mb-12">
            <div>
              <div className="text-lg font-semibold mb-4">CrucibAI</div>
              <p className="text-sm text-zinc-500">Turn ideas into software.</p>
            </div>
            
            <div>
              <div className="text-xs text-zinc-500 uppercase tracking-wider mb-4">Product</div>
              <ul className="space-y-3 text-sm">
                <li><a href="#" className="text-zinc-400 hover:text-white transition">Features</a></li>
                <li><a href="#" className="text-zinc-400 hover:text-white transition">Pricing</a></li>
                <li><a href="#" className="text-zinc-400 hover:text-white transition">Examples</a></li>
              </ul>
            </div>
            
            <div>
              <div className="text-xs text-zinc-500 uppercase tracking-wider mb-4">Company</div>
              <ul className="space-y-3 text-sm">
                <li><a href="#" className="text-zinc-400 hover:text-white transition">About</a></li>
                <li><a href="#" className="text-zinc-400 hover:text-white transition">Blog</a></li>
                <li><a href="#" className="text-zinc-400 hover:text-white transition">Careers</a></li>
              </ul>
            </div>
            
            <div>
              <div className="text-xs text-zinc-500 uppercase tracking-wider mb-4">Legal</div>
              <ul className="space-y-3 text-sm">
                <li><a href="#" className="text-zinc-400 hover:text-white transition">Privacy</a></li>
                <li><a href="#" className="text-zinc-400 hover:text-white transition">Terms</a></li>
              </ul>
            </div>
          </div>
          
          <div className="pt-8 border-t border-zinc-800/50 text-center">
            <p className="text-xs text-zinc-600">© 2026 CrucibAI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
