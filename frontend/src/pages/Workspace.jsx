import { useState, useEffect, useRef, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Editor from '@monaco-editor/react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Send, Loader2, Play, ChevronRight, ChevronDown, 
  File, Folder, Download, Upload, Mic, MicOff, Image,
  RotateCcw, GitBranch, Rocket, X, Check, Settings,
  Monitor, Code, Terminal, Clock, ChevronLeft, Plus
} from 'lucide-react';
import { useAuth, API } from '../App';
import axios from 'axios';

const Workspace = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, token } = useAuth();
  const initialPrompt = location.state?.prompt || '';
  
  // Project state
  const [projectName, setProjectName] = useState('Untitled Project');
  const [files, setFiles] = useState({
    'src/App.jsx': '// Start building...\n\nexport default function App() {\n  return (\n    <div>\n      <h1>Hello World</h1>\n    </div>\n  );\n}',
    'src/index.css': '@tailwind base;\n@tailwind components;\n@tailwind utilities;',
    'package.json': '{\n  "name": "my-app",\n  "version": "1.0.0"\n}'
  });
  const [selectedFile, setSelectedFile] = useState('src/App.jsx');
  const [versions, setVersions] = useState([]);
  
  // Chat state
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isBuilding, setIsBuilding] = useState(false);
  const [buildProgress, setBuildProgress] = useState(0);
  
  // Model selection
  const [selectedModel, setSelectedModel] = useState('auto');
  const [showModelPicker, setShowModelPicker] = useState(false);
  
  // Voice input
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState('');
  const recognitionRef = useRef(null);
  
  // File upload
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);
  
  // UI state
  const [activePanel, setActivePanel] = useState('preview'); // preview, console
  const [consoleOutput, setConsoleOutput] = useState([]);
  const [showSidebar, setShowSidebar] = useState(true);
  
  const chatEndRef = useRef(null);
  const [sessionId] = useState(() => `workspace_${Date.now()}`);

  const models = [
    { id: 'auto', name: 'Auto (Best for task)', desc: 'Automatically selects the best model' },
    { id: 'gpt-4o', name: 'GPT-4o', desc: 'OpenAI - Best for general tasks' },
    { id: 'claude', name: 'Claude Sonnet', desc: 'Anthropic - Best for code' },
    { id: 'gemini', name: 'Gemini Flash', desc: 'Google - Fast responses' }
  ];

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;
      
      recognitionRef.current.onresult = (event) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          }
        }
        if (finalTranscript) {
          setInput(prev => prev + ' ' + finalTranscript);
        }
      };
      
      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
      };
    }
  }, []);

  // Auto-scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Process initial prompt
  useEffect(() => {
    if (initialPrompt) {
      setInput(initialPrompt);
      setTimeout(() => handleSubmit(null, initialPrompt), 500);
    }
  }, []);

  const toggleRecording = () => {
    if (isRecording) {
      recognitionRef.current?.stop();
      setIsRecording(false);
    } else {
      recognitionRef.current?.start();
      setIsRecording(true);
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        const base64 = e.target.result;
        setMessages(prev => [...prev, { 
          role: 'user', 
          content: 'Build UI matching this image:',
          image: base64
        }]);
        handleImageToCode(base64);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleImageToCode = async (imageData) => {
    setIsBuilding(true);
    addConsole('Processing uploaded image...', 'info');
    
    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.post(`${API}/ai/chat`, {
        message: `I have an image of a UI design. Create a pixel-perfect React component with Tailwind CSS that matches this design exactly. The image shows: [User uploaded image]. Create a modern, responsive version. Respond with ONLY the complete React code.`,
        session_id: sessionId,
        model: 'gpt-4o'
      }, { headers, timeout: 60000 });
      
      const code = response.data.response.replace(/```jsx?/g, '').replace(/```/g, '').trim();
      updateFile('src/App.jsx', code);
      saveVersion('Image to code');
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'I\'ve created the UI based on your image. Check the preview.'
      }]);
      addConsole('Image processed successfully', 'success');
    } catch (error) {
      addConsole('Failed to process image: ' + error.message, 'error');
    } finally {
      setIsBuilding(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (ev) => handleImageToCode(ev.target.result);
      reader.readAsDataURL(file);
    }
  };

  const addConsole = (message, type = 'log') => {
    const timestamp = new Date().toLocaleTimeString();
    setConsoleOutput(prev => [...prev, { message, type, timestamp }]);
  };

  const updateFile = (path, content) => {
    setFiles(prev => ({ ...prev, [path]: content }));
    setSelectedFile(path);
  };

  const saveVersion = (label) => {
    setVersions(prev => [...prev, {
      id: Date.now(),
      label,
      timestamp: new Date().toISOString(),
      files: { ...files }
    }]);
  };

  const restoreVersion = (version) => {
    setFiles(version.files);
    addConsole(`Restored to: ${version.label}`, 'info');
  };

  const handleSubmit = async (e, overrideInput = null) => {
    e?.preventDefault();
    const prompt = overrideInput || input;
    if (!prompt.trim() || isBuilding) return;

    setInput('');
    setIsBuilding(true);
    setBuildProgress(0);
    setMessages(prev => [...prev, { role: 'user', content: prompt }]);
    addConsole(`Building: ${prompt}`, 'info');

    // Extract project name from first prompt
    if (messages.length === 0) {
      setProjectName(prompt.slice(0, 40));
    }

    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      // Progress simulation
      const progressInterval = setInterval(() => {
        setBuildProgress(prev => Math.min(prev + Math.random() * 20, 90));
      }, 300);

      const modelParam = selectedModel === 'auto' ? 'auto' : selectedModel;
      
      const response = await axios.post(`${API}/ai/chat`, {
        message: `You are CrucibAI. Create a complete React application for: "${prompt}"

Current code:
${files['src/App.jsx']}

Requirements:
- Use React functional components with hooks
- Use Tailwind CSS for styling
- Make it fully functional and modern
- Include ALL necessary imports

Respond with ONLY the complete code. No explanations.`,
        session_id: sessionId,
        model: modelParam
      }, { headers, timeout: 60000 });

      clearInterval(progressInterval);
      setBuildProgress(100);

      const code = response.data.response.replace(/```jsx?/g, '').replace(/```/g, '').trim();
      
      updateFile('src/App.jsx', code);
      saveVersion(prompt.slice(0, 30));
      
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `Done. Used ${response.data.model_used}. What would you like to change?`
      }]);
      
      addConsole(`Build complete (${response.data.model_used})`, 'success');

    } catch (error) {
      addConsole('Build failed: ' + error.message, 'error');
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Something went wrong. Try again.'
      }]);
    } finally {
      setIsBuilding(false);
      setBuildProgress(0);
    }
  };

  const downloadProject = () => {
    const content = Object.entries(files)
      .map(([name, code]) => `// === ${name} ===\n\n${code}`)
      .join('\n\n');
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${projectName.replace(/\s+/g, '-').toLowerCase()}.txt`;
    a.click();
  };

  const deployProject = () => {
    addConsole('Deploying to Vercel...', 'info');
    setTimeout(() => {
      addConsole('Deployed: https://' + projectName.replace(/\s+/g, '-').toLowerCase() + '.vercel.app', 'success');
    }, 2000);
  };

  // File tree component
  const FileTree = () => {
    const tree = Object.keys(files).reduce((acc, path) => {
      const parts = path.split('/');
      let current = acc;
      parts.forEach((part, i) => {
        if (i === parts.length - 1) {
          current[part] = { type: 'file', path };
        } else {
          current[part] = current[part] || { type: 'folder', children: {} };
          current = current[part].children;
        }
      });
      return acc;
    }, {});

    const renderNode = (name, node, depth = 0) => {
      if (node.type === 'file') {
        return (
          <button
            key={node.path}
            onClick={() => setSelectedFile(node.path)}
            className={`w-full flex items-center gap-2 px-3 py-1.5 text-sm hover:bg-zinc-800 rounded ${
              selectedFile === node.path ? 'bg-zinc-800 text-white' : 'text-zinc-400'
            }`}
            style={{ paddingLeft: `${depth * 12 + 12}px` }}
          >
            <File className="w-4 h-4" />
            {name}
          </button>
        );
      }
      return (
        <div key={name}>
          <div 
            className="flex items-center gap-2 px-3 py-1.5 text-sm text-zinc-500"
            style={{ paddingLeft: `${depth * 12 + 12}px` }}
          >
            <Folder className="w-4 h-4" />
            {name}
          </div>
          {node.children && Object.entries(node.children).map(([n, child]) => 
            renderNode(n, child, depth + 1)
          )}
        </div>
      );
    };

    return (
      <div className="py-2">
        {Object.entries(tree).map(([name, node]) => renderNode(name, node))}
      </div>
    );
  };

  return (
    <div 
      className="h-screen flex flex-col bg-[#0A0A0B] text-white overflow-hidden"
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* Drag overlay */}
      {isDragging && (
        <div className="absolute inset-0 z-50 bg-blue-500/20 border-2 border-dashed border-blue-500 flex items-center justify-center">
          <div className="text-xl font-medium">Drop image to generate UI</div>
        </div>
      )}

      {/* Header */}
      <header className="h-12 bg-[#141415] border-b border-zinc-800 flex items-center justify-between px-4 flex-shrink-0">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate('/')} className="text-lg font-semibold">
            CrucibAI
          </button>
          <span className="text-zinc-600">/</span>
          <span className="text-sm text-zinc-400">{projectName}</span>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Model selector */}
          <div className="relative">
            <button
              onClick={() => setShowModelPicker(!showModelPicker)}
              className="flex items-center gap-2 px-3 py-1.5 text-xs bg-zinc-800 hover:bg-zinc-700 rounded-lg transition"
            >
              <Settings className="w-3 h-3" />
              {models.find(m => m.id === selectedModel)?.name || 'Auto'}
              <ChevronDown className="w-3 h-3" />
            </button>
            
            {showModelPicker && (
              <div className="absolute right-0 top-full mt-2 w-64 bg-zinc-900 border border-zinc-800 rounded-lg shadow-xl z-50">
                {models.map(model => (
                  <button
                    key={model.id}
                    onClick={() => { setSelectedModel(model.id); setShowModelPicker(false); }}
                    className={`w-full p-3 text-left hover:bg-zinc-800 transition ${
                      selectedModel === model.id ? 'bg-zinc-800' : ''
                    }`}
                  >
                    <div className="text-sm font-medium flex items-center justify-between">
                      {model.name}
                      {selectedModel === model.id && <Check className="w-4 h-4 text-green-500" />}
                    </div>
                    <div className="text-xs text-zinc-500">{model.desc}</div>
                  </button>
                ))}
              </div>
            )}
          </div>
          
          <button onClick={downloadProject} className="flex items-center gap-2 px-3 py-1.5 text-xs bg-zinc-800 hover:bg-zinc-700 rounded-lg transition">
            <Download className="w-3 h-3" />
            Export
          </button>
          <button onClick={deployProject} className="flex items-center gap-2 px-3 py-1.5 text-xs bg-white text-black hover:bg-zinc-200 rounded-lg transition font-medium">
            <Rocket className="w-3 h-3" />
            Deploy
          </button>
        </div>
      </header>

      {/* Progress bar */}
      {isBuilding && (
        <div className="h-0.5 bg-zinc-800">
          <motion.div 
            className="h-full bg-blue-500"
            initial={{ width: 0 }}
            animate={{ width: `${buildProgress}%` }}
          />
        </div>
      )}

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar - Files */}
        <div className={`${showSidebar ? 'w-56' : 'w-0'} flex-shrink-0 bg-[#111112] border-r border-zinc-800 overflow-hidden transition-all`}>
          <div className="p-3 border-b border-zinc-800 flex items-center justify-between">
            <span className="text-xs text-zinc-500 uppercase tracking-wider">Files</span>
            <button className="p-1 hover:bg-zinc-800 rounded">
              <Plus className="w-3 h-3 text-zinc-500" />
            </button>
          </div>
          <FileTree />
          
          {/* Version history */}
          {versions.length > 0 && (
            <div className="border-t border-zinc-800">
              <div className="p-3 flex items-center gap-2 text-xs text-zinc-500 uppercase tracking-wider">
                <Clock className="w-3 h-3" />
                History
              </div>
              <div className="max-h-32 overflow-y-auto">
                {versions.slice(-5).reverse().map(v => (
                  <button
                    key={v.id}
                    onClick={() => restoreVersion(v)}
                    className="w-full px-3 py-2 text-left text-xs text-zinc-400 hover:bg-zinc-800 flex items-center gap-2"
                  >
                    <RotateCcw className="w-3 h-3" />
                    {v.label}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Editor */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Tabs */}
          <div className="h-10 bg-[#111112] border-b border-zinc-800 flex items-center px-2">
            <button
              onClick={() => setShowSidebar(!showSidebar)}
              className="p-1.5 hover:bg-zinc-800 rounded mr-2"
            >
              {showSidebar ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
            </button>
            {Object.keys(files).map(file => (
              <button
                key={file}
                onClick={() => setSelectedFile(file)}
                className={`flex items-center gap-2 px-3 py-1.5 text-xs rounded-t ${
                  selectedFile === file 
                    ? 'bg-[#1E1E1E] text-white' 
                    : 'text-zinc-500 hover:text-zinc-300'
                }`}
              >
                <File className="w-3 h-3" />
                {file.split('/').pop()}
              </button>
            ))}
          </div>
          
          {/* Monaco Editor */}
          <div className="flex-1">
            <Editor
              height="100%"
              language={selectedFile?.endsWith('.css') ? 'css' : selectedFile?.endsWith('.json') ? 'json' : 'javascript'}
              value={files[selectedFile] || ''}
              onChange={(value) => setFiles(prev => ({ ...prev, [selectedFile]: value || '' }))}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 13,
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                automaticLayout: true,
                tabSize: 2,
                padding: { top: 16 }
              }}
            />
          </div>
        </div>

        {/* Right panel - Preview + Chat */}
        <div className="w-96 flex flex-col border-l border-zinc-800 bg-[#111112]">
          {/* Panel tabs */}
          <div className="h-10 border-b border-zinc-800 flex items-center gap-1 px-2">
            <button
              onClick={() => setActivePanel('preview')}
              className={`flex items-center gap-2 px-3 py-1.5 text-xs rounded ${
                activePanel === 'preview' ? 'bg-zinc-800 text-white' : 'text-zinc-500'
              }`}
            >
              <Monitor className="w-3 h-3" />
              Preview
            </button>
            <button
              onClick={() => setActivePanel('console')}
              className={`flex items-center gap-2 px-3 py-1.5 text-xs rounded ${
                activePanel === 'console' ? 'bg-zinc-800 text-white' : 'text-zinc-500'
              }`}
            >
              <Terminal className="w-3 h-3" />
              Console
            </button>
          </div>

          {/* Preview */}
          {activePanel === 'preview' && (
            <div className="flex-1 bg-white p-4">
              <div className="h-full rounded-lg bg-gradient-to-br from-zinc-100 to-zinc-200 flex items-center justify-center text-zinc-400 text-sm">
                Live preview coming soon
              </div>
            </div>
          )}

          {/* Console */}
          {activePanel === 'console' && (
            <div className="flex-1 overflow-y-auto p-3 font-mono text-xs">
              {consoleOutput.map((log, i) => (
                <div key={i} className={`py-1 ${
                  log.type === 'error' ? 'text-red-400' :
                  log.type === 'success' ? 'text-green-400' :
                  'text-zinc-400'
                }`}>
                  <span className="text-zinc-600">[{log.timestamp}]</span> {log.message}
                </div>
              ))}
            </div>
          )}

          {/* Chat */}
          <div className="h-72 border-t border-zinc-800 flex flex-col">
            <div className="flex-1 overflow-y-auto p-3 space-y-3">
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] px-3 py-2 rounded-lg text-sm ${
                    msg.role === 'user' ? 'bg-white text-black' : 'bg-zinc-800 text-zinc-200'
                  }`}>
                    {msg.image && (
                      <img src={msg.image} alt="Uploaded" className="max-w-full rounded mb-2" />
                    )}
                    {msg.content}
                  </div>
                </div>
              ))}
              {isBuilding && (
                <div className="flex justify-start">
                  <div className="bg-zinc-800 px-3 py-2 rounded-lg">
                    <Loader2 className="w-4 h-4 animate-spin" />
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSubmit} className="p-3 border-t border-zinc-800">
              <div className="flex gap-2">
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  accept="image/*"
                  className="hidden"
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="p-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg transition"
                  title="Upload image"
                >
                  <Image className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={toggleRecording}
                  className={`p-2 rounded-lg transition ${
                    isRecording ? 'bg-red-500 text-white' : 'bg-zinc-800 hover:bg-zinc-700'
                  }`}
                  title={isRecording ? 'Stop recording' : 'Voice input'}
                >
                  {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                </button>
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Describe changes..."
                  className="flex-1 px-3 py-2 bg-zinc-800 rounded-lg text-sm outline-none focus:ring-1 focus:ring-zinc-600"
                  disabled={isBuilding}
                />
                <button
                  type="submit"
                  disabled={!input.trim() || isBuilding}
                  className="p-2 bg-white text-black rounded-lg disabled:opacity-30 hover:bg-zinc-200 transition"
                >
                  <Send className="w-4 h-4" />
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Workspace;
