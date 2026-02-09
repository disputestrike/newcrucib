import { useState, useRef, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, Send, Loader2, Sparkles, Play, ArrowRight, Check, Menu, X, Code, Layers, Zap, Globe, Shield, Database, Mic, Paperclip, Image, StopCircle } from 'lucide-react';
import { useAuth, API } from '../App';
import axios from 'axios';

const LandingPage = () => {
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [openFaq, setOpenFaq] = useState(null);
  
  // Chat/Build state
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isBuilding, setIsBuilding] = useState(false);
  const [buildProgress, setBuildProgress] = useState(0);
  const [projectName, setProjectName] = useState('');
  const [generatedCode, setGeneratedCode] = useState(null);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const chatEndRef = useRef(null);
  const inputRef = useRef(null);

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

    // Extract project name from prompt
    const name = userPrompt.split(' ').slice(0, 3).join(' ');
    setProjectName(name);

    // Add building message
    setMessages(prev => [...prev, { 
      role: 'assistant', 
      content: `Building "${name}"...`,
      isBuilding: true
    }]);

    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      // Simulate progress while AI works
      const progressInterval = setInterval(() => {
        setBuildProgress(prev => Math.min(prev + Math.random() * 15, 90));
      }, 500);

      // Get AI to generate the app
      const response = await axios.post(`${API}/ai/chat`, {
        message: `You are CrucibAI, an expert app builder. Create a complete, production-ready React application for: "${userPrompt}"

Requirements:
- Use React with hooks (useState, useEffect)
- Use Tailwind CSS for modern, beautiful styling
- Make it fully functional and interactive
- Include all necessary imports
- Create a complete, working component

Respond with ONLY the complete React code. No explanations. Start with imports.`,
        session_id: sessionId,
        model: 'auto'
      }, { headers, timeout: 60000 });

      clearInterval(progressInterval);
      setBuildProgress(100);

      const code = response.data.response
        .replace(/```jsx?/g, '')
        .replace(/```/g, '')
        .trim();

      setGeneratedCode({
        name: name,
        code: code,
        model: response.data.model_used
      });

      // Update the building message to complete
      setMessages(prev => prev.map((msg, i) => 
        i === prev.length - 1 
          ? { 
              role: 'assistant', 
              content: `✅ **"${name}"** is ready!\n\nI've built your app with React and Tailwind CSS. You can:\n• View the generated code below\n• Download it as a project\n• Ask me to make changes\n\nWhat would you like to modify?`,
              isBuilding: false,
              hasCode: true
            }
          : msg
      ));

    } catch (error) {
      setMessages(prev => prev.map((msg, i) => 
        i === prev.length - 1 
          ? { role: 'assistant', content: `Sorry, I encountered an error. Please try again.`, error: true }
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
      // If we already have code, this is a modification request
      modifyCode(input);
    } else {
      // Start a new build
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
        message: `Current React code:\n\n${generatedCode.code}\n\nUser wants to: "${request}"\n\nProvide the COMPLETE updated code with this change. Respond with ONLY code, no explanations.`,
        session_id: sessionId,
        model: 'auto'
      }, { headers, timeout: 60000 });

      const newCode = response.data.response
        .replace(/```jsx?/g, '')
        .replace(/```/g, '')
        .trim();

      if (newCode.includes('import') || newCode.includes('function') || newCode.includes('const')) {
        setGeneratedCode(prev => ({ ...prev, code: newCode }));
        setMessages(prev => prev.map((msg, i) => 
          i === prev.length - 1 
            ? { role: 'assistant', content: `✅ Done! I've updated the code. What else would you like to change?`, hasCode: true }
            : msg
        ));
      } else {
        setMessages(prev => prev.map((msg, i) => 
          i === prev.length - 1 
            ? { role: 'assistant', content: response.data.response }
            : msg
        ));
      }
    } catch (error) {
      setMessages(prev => prev.map((msg, i) => 
        i === prev.length - 1 
          ? { role: 'assistant', content: 'Sorry, something went wrong. Try again.', error: true }
          : msg
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
    a.download = `${generatedCode.name.replace(/\s+/g, '-').toLowerCase()}.jsx`;
    a.click();
  };

  const features = [
    { icon: Code, title: 'Build websites and apps', desc: 'Describe what you want and CrucibAI builds it instantly with production-ready code.' },
    { icon: Sparkles, title: 'Powered by latest AI', desc: 'GPT-4o, Claude, and Gemini working together to create the best results.' },
    { icon: Layers, title: 'Iterate with conversation', desc: 'Just tell CrucibAI what to change. No coding required.' }
  ];

  const faqs = [
    { q: 'What is CrucibAI?', a: 'CrucibAI is an AI app builder. Describe what you want in plain English, and it creates fully functional applications for you instantly.' },
    { q: 'Do I need coding experience?', a: 'No! Just describe what you want to build. CrucibAI handles all the technical work.' },
    { q: 'What can I build?', a: 'Websites, web apps, dashboards, landing pages, tools - anything you can describe.' },
    { q: 'How do I make changes?', a: 'Just tell CrucibAI what to modify. Say "add dark mode" or "change the color to blue" and it updates the code.' }
  ];

  return (
    <div className="min-h-screen bg-white text-gray-900">
      {/* Navbar */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2">
            <span className="text-2xl font-bold tracking-tight">Crucib<span className="text-blue-600">AI</span></span>
          </Link>
          
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-gray-600 hover:text-gray-900 transition font-medium">Features</a>
            <a href="#faq" className="text-gray-600 hover:text-gray-900 transition font-medium">FAQs</a>
          </div>

          <div className="hidden md:flex items-center gap-4">
            {user ? (
              <button onClick={() => navigate('/app')} className="px-5 py-2.5 bg-gray-900 hover:bg-gray-800 text-white rounded-full font-medium transition" data-testid="go-to-dashboard-btn">
                Dashboard
              </button>
            ) : (
              <>
                <button onClick={() => navigate('/auth')} className="px-5 py-2.5 text-gray-600 hover:text-gray-900 transition font-medium" data-testid="login-btn">
                  Sign in
                </button>
                <button onClick={() => navigate('/auth?mode=register')} className="px-5 py-2.5 bg-gray-900 hover:bg-gray-800 text-white rounded-full font-medium transition" data-testid="get-started-btn">
                  Get Started
                </button>
              </>
            )}
          </div>

          <button className="md:hidden p-2" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
            {mobileMenuOpen ? <X /> : <Menu />}
          </button>
        </div>
      </nav>

      {/* Hero + Chat */}
      <section className="pt-28 pb-16 px-6">
        <div className="max-w-4xl mx-auto">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-12"
          >
            <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight tracking-tight">
              What do you want to build?
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Describe your idea and CrucibAI will build it for you.
            </p>
          </motion.div>

          {/* Chat Interface */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-2xl border border-gray-200 shadow-xl overflow-hidden"
          >
            {/* Messages */}
            <div className="min-h-[300px] max-h-[500px] overflow-y-auto p-6" data-testid="chat-messages">
              {messages.length === 0 ? (
                <div className="text-center py-12">
                  <Sparkles className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">Describe what you want to create...</p>
                  <div className="mt-6 flex flex-wrap justify-center gap-2">
                    {['A todo app', 'Portfolio website', 'Dashboard with charts', 'Landing page'].map(suggestion => (
                      <button
                        key={suggestion}
                        onClick={() => setInput(suggestion)}
                        className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700 transition"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {messages.map((msg, i) => (
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
                            : 'bg-gray-100 text-gray-800'
                      }`}>
                        {msg.isBuilding ? (
                          <div className="flex items-center gap-3">
                            <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
                            <span>{msg.content}</span>
                          </div>
                        ) : (
                          <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</p>
                        )}
                      </div>
                    </motion.div>
                  ))}
                  <div ref={chatEndRef} />
                </div>
              )}
            </div>

            {/* Progress bar when building */}
            {isBuilding && (
              <div className="px-6 pb-2">
                <div className="h-1 bg-gray-100 rounded-full overflow-hidden">
                  <motion.div 
                    className="h-full bg-blue-600"
                    initial={{ width: 0 }}
                    animate={{ width: `${buildProgress}%` }}
                    transition={{ duration: 0.3 }}
                  />
                </div>
              </div>
            )}

            {/* Generated Code Preview */}
            {generatedCode && !isBuilding && (
              <div className="px-6 pb-4">
                <div className="bg-gray-900 rounded-xl p-4 max-h-64 overflow-auto">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs text-gray-400 font-mono">{generatedCode.name}.jsx</span>
                    <button 
                      onClick={downloadCode}
                      className="text-xs text-blue-400 hover:text-blue-300"
                    >
                      Download
                    </button>
                  </div>
                  <pre className="text-xs text-gray-300 font-mono overflow-x-auto">
                    <code>{generatedCode.code.slice(0, 1000)}{generatedCode.code.length > 1000 ? '...' : ''}</code>
                  </pre>
                </div>
              </div>
            )}

            {/* Input */}
            <form onSubmit={handleSubmit} className="p-4 border-t border-gray-100 bg-gray-50">
              <div className="flex items-center gap-3">
                <div className="flex-1 relative">
                  <input
                    ref={inputRef}
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder={generatedCode ? "Ask for changes..." : "Describe what you want to build..."}
                    className="w-full px-4 py-3 pr-24 bg-white border border-gray-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 outline-none transition"
                    disabled={isBuilding}
                    data-testid="main-input"
                  />
                  <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
                    <button type="button" className="p-2 hover:bg-gray-100 rounded-lg transition" title="Voice input">
                      <Mic className="w-4 h-4 text-gray-400" />
                    </button>
                    <button type="button" className="p-2 hover:bg-gray-100 rounded-lg transition" title="Attach file">
                      <Paperclip className="w-4 h-4 text-gray-400" />
                    </button>
                  </div>
                </div>
                <button
                  type="submit"
                  disabled={!input.trim() || isBuilding}
                  className="px-5 py-3 bg-gray-900 hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-xl transition flex items-center gap-2 font-medium"
                  data-testid="send-btn"
                >
                  {isBuilding ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </button>
              </div>
            </form>
          </motion.div>

          <p className="text-center text-sm text-gray-500 mt-4">
            Free to use • No sign-up required • Powered by GPT-4o & Claude
          </p>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 px-6 bg-gray-50">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">How CrucibAI works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="text-center"
              >
                <div className="w-14 h-14 bg-gray-900 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <feature.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="py-20 px-6">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Questions?</h2>
          <div className="space-y-3">
            {faqs.map((faq, i) => (
              <div key={i} className="border border-gray-200 rounded-xl overflow-hidden">
                <button
                  onClick={() => setOpenFaq(openFaq === i ? null : i)}
                  className="w-full p-5 flex items-center justify-between text-left bg-white hover:bg-gray-50 transition"
                >
                  <span className="font-medium">{faq.q}</span>
                  <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${openFaq === i ? 'rotate-180' : ''}`} />
                </button>
                <AnimatePresence>
                  {openFaq === i && (
                    <motion.div
                      initial={{ height: 0 }}
                      animate={{ height: 'auto' }}
                      exit={{ height: 0 }}
                      className="overflow-hidden"
                    >
                      <p className="px-5 pb-5 text-gray-600">{faq.a}</p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-gray-100">
        <div className="max-w-5xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <span className="text-xl font-bold tracking-tight">Crucib<span className="text-blue-600">AI</span></span>
          <p className="text-gray-500 text-sm">© 2026 CrucibAI. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
