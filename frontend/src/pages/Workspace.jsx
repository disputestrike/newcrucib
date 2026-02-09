import { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate, useSearchParams, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import Editor from '@monaco-editor/react';
import {
  SandpackProvider,
  SandpackPreview,
} from '@codesandbox/sandpack-react';
import {
  ChevronDown,
  Send,
  Loader2,
  ArrowLeft,
  Download,
  Copy,
  Check,
  Mic,
  MicOff,
  Paperclip,
  X,
  FileCode,
  FolderOpen,
  Terminal,
  Eye,
  Maximize2,
  Minimize2,
  Sparkles,
  Image,
  FileText,
  File,
  Coffee,
  Zap,
  RefreshCw,
  ExternalLink,
  Github,
  History,
  Undo2
} from 'lucide-react';
import { useAuth, API } from '../App';
import axios from 'axios';

// Default React app template
const DEFAULT_FILES = {
  '/App.js': {
    code: `import React from 'react';

export default function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-4">
          Welcome to CrucibAI
        </h1>
        <p className="text-slate-400 text-lg">
          Describe what you want to build in the chat...
        </p>
      </div>
    </div>
  );
}`,
  },
  '/index.js': {
    code: `import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);`,
  },
  '/styles.css': {
    code: `@import url('https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css');

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}`,
  },
};

// File tree component
const FileTree = ({ files, activeFile, onSelectFile }) => {
  const getFileIcon = (filename) => {
    if (filename.endsWith('.js') || filename.endsWith('.jsx')) return <FileCode className="w-4 h-4 text-yellow-400" />;
    if (filename.endsWith('.css')) return <FileText className="w-4 h-4 text-blue-400" />;
    if (filename.endsWith('.html')) return <FileText className="w-4 h-4 text-orange-400" />;
    return <File className="w-4 h-4 text-zinc-400" />;
  };

  const fileList = Object.keys(files).sort();

  return (
    <div className="text-sm">
      <div className="flex items-center gap-2 px-3 py-2 text-zinc-400 text-xs uppercase tracking-wider">
        <FolderOpen className="w-4 h-4" />
        <span>Files</span>
      </div>
      {fileList.map((filename) => (
        <button
          key={filename}
          onClick={() => onSelectFile(filename)}
          data-testid={`file-${filename.replace('/', '')}`}
          className={`w-full flex items-center gap-2 px-4 py-1.5 text-left transition ${
            activeFile === filename
              ? 'bg-zinc-800 text-white'
              : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200'
          }`}
        >
          {getFileIcon(filename)}
          <span className="truncate">{filename.replace('/', '')}</span>
        </button>
      ))}
    </div>
  );
};

// Console/Logs component
const ConsolePanel = ({ logs }) => {
  const consoleRef = useRef(null);

  useEffect(() => {
    if (consoleRef.current) {
      consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div ref={consoleRef} className="h-full overflow-auto font-mono text-xs p-3 space-y-1">
      {logs.length === 0 ? (
        <div className="text-zinc-600">Console output will appear here...</div>
      ) : (
        logs.map((log, i) => (
          <div
            key={i}
            className={`flex items-start gap-2 ${
              log.type === 'error' ? 'text-red-400' :
              log.type === 'success' ? 'text-green-400' :
              log.type === 'warning' ? 'text-yellow-400' :
              'text-zinc-400'
            }`}
          >
            <span className="text-zinc-600">[{log.time}]</span>
            <span className="text-zinc-500">{log.agent || 'system'}:</span>
            <span className="flex-1">{log.message}</span>
          </div>
        ))
      )}
    </div>
  );
};

// LLM Selector dropdown
const ModelSelector = ({ selectedModel, onSelectModel }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  const models = [
    { id: 'auto', name: 'Auto Select', icon: Sparkles, desc: 'Best model for the task' },
    { id: 'gpt-4o', name: 'GPT-4o', icon: Zap, desc: 'OpenAI latest' },
    { id: 'claude', name: 'Claude 3.5', icon: Coffee, desc: 'Anthropic Sonnet' },
    { id: 'gemini', name: 'Gemini Flash', icon: RefreshCw, desc: 'Google fast model' },
  ];

  const selected = models.find(m => m.id === selectedModel) || models[0];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        data-testid="model-selector"
        className="flex items-center gap-2 px-3 py-1.5 bg-zinc-800/50 rounded-lg text-sm text-zinc-300 hover:bg-zinc-800 transition"
      >
        <selected.icon className="w-4 h-4" />
        <span>{selected.name}</span>
        <ChevronDown className={`w-3 h-3 transition ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute bottom-full left-0 mb-2 w-56 bg-zinc-900 border border-zinc-800 rounded-lg shadow-xl overflow-hidden z-50"
          >
            {models.map((model) => (
              <button
                key={model.id}
                onClick={() => { onSelectModel(model.id); setIsOpen(false); }}
                data-testid={`model-option-${model.id}`}
                className={`w-full flex items-center gap-3 px-4 py-3 text-left transition ${
                  selectedModel === model.id ? 'bg-zinc-800 text-white' : 'text-zinc-400 hover:bg-zinc-800/50'
                }`}
              >
                <model.icon className="w-4 h-4" />
                <div>
                  <div className="text-sm font-medium">{model.name}</div>
                  <div className="text-xs text-zinc-500">{model.desc}</div>
                </div>
                {selectedModel === model.id && <Check className="w-4 h-4 ml-auto text-green-400" />}
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

// Version History Panel
const VersionHistory = ({ versions, onRestore, currentVersion }) => {
  return (
    <div className="p-3 space-y-2 overflow-y-auto h-full">
      <div className="text-xs text-zinc-500 uppercase tracking-wider mb-3">Version History</div>
      {versions.length === 0 ? (
        <div className="text-sm text-zinc-600">No versions yet</div>
      ) : (
        versions.map((version, i) => (
          <div
            key={version.id}
            className={`p-3 rounded-lg cursor-pointer transition ${
              currentVersion === version.id ? 'bg-zinc-800 border border-zinc-700' : 'bg-zinc-800/30 hover:bg-zinc-800/60'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-zinc-200">v{versions.length - i}</span>
              <span className="text-xs text-zinc-500">{version.time}</span>
            </div>
            <p className="text-xs text-zinc-400 mb-2 line-clamp-2">{version.prompt}</p>
            {currentVersion !== version.id && (
              <button
                onClick={() => onRestore(version)}
                className="flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
              >
                <Undo2 className="w-3 h-3" />
                Restore
              </button>
            )}
          </div>
        ))
      )}
    </div>
  );
};

// Main Workspace Component
const Workspace = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { user, token } = useAuth();
  
  const [files, setFiles] = useState(DEFAULT_FILES);
  const [activeFile, setActiveFile] = useState('/App.js');
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isBuilding, setIsBuilding] = useState(false);
  const [buildProgress, setBuildProgress] = useState(0);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [selectedModel, setSelectedModel] = useState('auto');
  const [logs, setLogs] = useState([]);
  const [copied, setCopied] = useState(false);
  const [activePanel, setActivePanel] = useState('preview');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [versions, setVersions] = useState([]);
  const [currentVersion, setCurrentVersion] = useState(null);
  
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  
  const [attachedFiles, setAttachedFiles] = useState([]);
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    const initialPrompt = searchParams.get('prompt');
    if (initialPrompt) {
      setInput(initialPrompt);
      setTimeout(() => handleBuild(initialPrompt), 500);
    }
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const addLog = (message, type = 'info', agent = null) => {
    const now = new Date();
    const time = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')}:${now.getSeconds().toString().padStart(2, '0')}`;
    setLogs(prev => [...prev, { message, type, time, agent }]);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      const chunks = [];
      
      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunks.push(e.data);
      };
      
      recorder.onstop = async () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        stream.getTracks().forEach(track => track.stop());
        await transcribeAudio(blob);
      };
      
      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
      addLog('Voice recording started...', 'info', 'voice');
    } catch (err) {
      addLog('Microphone access denied', 'error', 'voice');
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
      setIsRecording(false);
      addLog('Processing voice input...', 'info', 'voice');
    }
  };

  const transcribeAudio = async (blob) => {
    try {
      const formData = new FormData();
      formData.append('audio', blob, 'recording.webm');
      
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      const response = await axios.post(`${API}/voice/transcribe`, formData, {
        headers: { ...headers, 'Content-Type': 'multipart/form-data' },
        timeout: 30000
      });
      
      if (response.data.text) {
        setInput(response.data.text);
        addLog(`Transcribed: "${response.data.text}"`, 'success', 'voice');
      }
    } catch (err) {
      addLog('Failed to transcribe audio', 'error', 'voice');
    }
  };

  const handleFileSelect = (e) => {
    const selectedFiles = Array.from(e.target.files);
    const validFiles = selectedFiles.filter(f => 
      f.type.startsWith('image/') || 
      f.type === 'application/pdf' ||
      f.type.startsWith('text/')
    );
    
    validFiles.forEach(file => {
      const reader = new FileReader();
      reader.onload = (e) => {
        setAttachedFiles(prev => [...prev, {
          name: file.name,
          type: file.type,
          data: e.target.result,
          size: file.size
        }]);
        addLog(`Attached: ${file.name}`, 'info', 'files');
      };
      if (file.type.startsWith('image/')) {
        reader.readAsDataURL(file);
      } else {
        reader.readAsText(file);
      }
    });
  };

  const removeFile = (index) => {
    setAttachedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleBuild = async (promptOverride = null) => {
    const prompt = promptOverride || input;
    if (!prompt.trim() || isBuilding) return;

    setInput('');
    setIsBuilding(true);
    setBuildProgress(0);
    
    const userMessage = { 
      role: 'user', 
      content: prompt,
      attachments: attachedFiles.length > 0 ? [...attachedFiles] : undefined
    };
    setMessages(prev => [...prev, userMessage]);
    setAttachedFiles([]);
    
    setMessages(prev => [...prev, { role: 'assistant', content: 'Building...', isBuilding: true }]);

    addLog('Starting build process...', 'info', 'planner');
    
    const agents = [
      { name: 'Planner', delay: 300 },
      { name: 'Frontend', delay: 500 },
      { name: 'Styling', delay: 400 },
      { name: 'Testing', delay: 300 },
      { name: 'Finalizing', delay: 200 }
    ];

    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      let progress = 0;
      for (const agent of agents) {
        addLog(`${agent.name} agent processing...`, 'info', agent.name.toLowerCase());
        await new Promise(r => setTimeout(r, agent.delay));
        progress += 20;
        setBuildProgress(Math.min(progress, 90));
      }

      let messageContent = `Create a complete, production-ready React application for: "${prompt}". 
Use React hooks and Tailwind CSS. Make it modern, responsive, and functional.
Include all necessary components and styling.
Respond with ONLY the complete App.js code, nothing else.`;

      if (attachedFiles.length > 0) {
        const imageFiles = attachedFiles.filter(f => f.type.startsWith('image/'));
        if (imageFiles.length > 0) {
          messageContent += `\n\nThe user has attached ${imageFiles.length} image(s) as reference. Try to match the design style.`;
        }
      }

      const response = await axios.post(`${API}/ai/chat`, {
        message: messageContent,
        session_id: sessionId,
        model: selectedModel
      }, { headers, timeout: 90000 });

      setBuildProgress(100);
      addLog('Build completed successfully!', 'success', 'deploy');

      let code = response.data.response;
      code = code.replace(/```jsx?/g, '').replace(/```/g, '').trim();

      const newFiles = { ...files, '/App.js': { code } };
      setFiles(newFiles);

      const newVersion = {
        id: `v_${Date.now()}`,
        prompt,
        files: newFiles,
        time: new Date().toLocaleTimeString()
      };
      setVersions(prev => [newVersion, ...prev]);
      setCurrentVersion(newVersion.id);

      setMessages(prev => prev.map((msg, i) => 
        i === prev.length - 1 
          ? { role: 'assistant', content: `Done! Your app is ready. What would you like to change?`, hasCode: true }
          : msg
      ));

    } catch (error) {
      addLog(`Build failed: ${error.message}`, 'error', 'system');
      setMessages(prev => prev.map((msg, i) => 
        i === prev.length - 1 
          ? { role: 'assistant', content: 'Something went wrong. Please try again.', error: true }
          : msg
      ));
    } finally {
      setIsBuilding(false);
    }
  };

  const handleModify = async () => {
    if (!input.trim() || isBuilding) return;

    const request = input.trim();
    setInput('');
    setIsBuilding(true);
    
    setMessages(prev => [...prev, { role: 'user', content: request }]);
    setMessages(prev => [...prev, { role: 'assistant', content: 'Updating...', isBuilding: true }]);
    
    addLog('Processing modification request...', 'info', 'planner');

    try {
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const response = await axios.post(`${API}/ai/chat`, {
        message: `Current code:\n\n${files['/App.js'].code}\n\nModify it to: "${request}"\n\nRespond with ONLY the complete updated App.js code, nothing else.`,
        session_id: sessionId,
        model: selectedModel
      }, { headers, timeout: 90000 });

      let newCode = response.data.response;
      newCode = newCode.replace(/```jsx?/g, '').replace(/```/g, '').trim();

      if (newCode.includes('import') || newCode.includes('function') || newCode.includes('const')) {
        const newFiles = { ...files, '/App.js': { code: newCode } };
        setFiles(newFiles);
        
        const newVersion = {
          id: `v_${Date.now()}`,
          prompt: request,
          files: newFiles,
          time: new Date().toLocaleTimeString()
        };
        setVersions(prev => [newVersion, ...prev]);
        setCurrentVersion(newVersion.id);
        
        addLog('Modification applied successfully!', 'success', 'frontend');
        
        setMessages(prev => prev.map((msg, i) => 
          i === prev.length - 1 ? { role: 'assistant', content: 'Updated! What else would you like to change?', hasCode: true } : msg
        ));
      } else {
        setMessages(prev => prev.map((msg, i) => 
          i === prev.length - 1 ? { role: 'assistant', content: response.data.response } : msg
        ));
      }
    } catch (error) {
      addLog(`Modification failed: ${error.message}`, 'error', 'system');
      setMessages(prev => prev.map((msg, i) => 
        i === prev.length - 1 ? { role: 'assistant', content: 'Error updating. Try again.', error: true } : msg
      ));
    } finally {
      setIsBuilding(false);
    }
  };

  const handleSubmit = (e) => {
    e?.preventDefault();
    if (!input.trim()) return;
    
    if (versions.length > 0) {
      handleModify();
    } else {
      handleBuild();
    }
  };

  const restoreVersion = (version) => {
    setFiles(version.files);
    setCurrentVersion(version.id);
    addLog(`Restored to version from ${version.time}`, 'info', 'history');
  };

  const downloadCode = () => {
    Object.entries(files).forEach(([name, { code }]) => {
      const blob = new Blob([code], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = name.replace('/', '');
      a.click();
    });
    addLog('Files downloaded', 'success', 'export');
  };

  const copyCode = () => {
    navigator.clipboard.writeText(files[activeFile].code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleCodeChange = (value) => {
    setFiles(prev => ({
      ...prev,
      [activeFile]: { code: value }
    }));
  };

  return (
    <div className="h-screen bg-[#0A0A0B] text-white flex flex-col overflow-hidden">
      {/* Header */}
      <header className="h-14 border-b border-zinc-800 flex items-center justify-between px-4 flex-shrink-0">
        <div className="flex items-center gap-4">
          <button 
            onClick={() => navigate('/')}
            data-testid="back-button"
            className="flex items-center gap-2 text-zinc-400 hover:text-white transition"
          >
            <ArrowLeft className="w-4 h-4" />
            <span className="text-lg font-semibold">CrucibAI</span>
          </button>
          
          <div className="h-4 w-px bg-zinc-800" />
          
          <div className="text-sm text-zinc-500">
            {versions.length > 0 ? `v${versions.length}` : 'New Project'}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <ModelSelector selectedModel={selectedModel} onSelectModel={setSelectedModel} />
          
          <button
            onClick={downloadCode}
            data-testid="export-button"
            className="flex items-center gap-2 px-3 py-1.5 bg-zinc-800/50 rounded-lg text-sm text-zinc-300 hover:bg-zinc-800 transition"
          >
            <Download className="w-4 h-4" />
            <span className="hidden sm:inline">Export</span>
          </button>
          
          <button 
            data-testid="github-button"
            className="flex items-center gap-2 px-3 py-1.5 bg-zinc-800/50 rounded-lg text-sm text-zinc-300 hover:bg-zinc-800 transition"
          >
            <Github className="w-4 h-4" />
            <span className="hidden sm:inline">Push</span>
          </button>
          
          <button 
            data-testid="deploy-button"
            className="flex items-center gap-2 px-4 py-1.5 bg-white text-black rounded-lg text-sm font-medium hover:bg-zinc-200 transition"
          >
            <ExternalLink className="w-4 h-4" />
            <span>Deploy</span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - File Explorer */}
        <div className="w-56 border-r border-zinc-800 flex-shrink-0 overflow-y-auto">
          <FileTree 
            files={files} 
            activeFile={activeFile} 
            onSelectFile={setActiveFile}
          />
        </div>

        {/* Code Editor */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Editor Tabs */}
          <div className="h-10 border-b border-zinc-800 flex items-center px-2 gap-1 flex-shrink-0">
            {Object.keys(files).map(filename => (
              <button
                key={filename}
                onClick={() => setActiveFile(filename)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm transition ${
                  activeFile === filename 
                    ? 'bg-zinc-800 text-white' 
                    : 'text-zinc-500 hover:text-zinc-300'
                }`}
              >
                <FileCode className="w-3.5 h-3.5" />
                {filename.replace('/', '')}
              </button>
            ))}
            
            <div className="ml-auto flex items-center gap-2">
              <button
                onClick={copyCode}
                className="p-1.5 text-zinc-500 hover:text-white transition"
                title="Copy code"
              >
                {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Monaco Editor */}
          <div className="flex-1">
            <Editor
              height="100%"
              language={activeFile.endsWith('.css') ? 'css' : 'javascript'}
              value={files[activeFile]?.code || ''}
              onChange={handleCodeChange}
              theme="vs-dark"
              options={{
                minimap: { enabled: false },
                fontSize: 13,
                lineNumbers: 'on',
                scrollBeyondLastLine: false,
                wordWrap: 'on',
                tabSize: 2,
                padding: { top: 16 },
              }}
            />
          </div>
        </div>

        {/* Right Panel - Preview / Console / History */}
        <div className="w-[45%] border-l border-zinc-800 flex flex-col flex-shrink-0">
          {/* Panel Tabs */}
          <div className="h-10 border-b border-zinc-800 flex items-center px-2 gap-1 flex-shrink-0">
            <button
              onClick={() => setActivePanel('preview')}
              data-testid="preview-tab"
              className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm transition ${
                activePanel === 'preview' ? 'bg-zinc-800 text-white' : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              <Eye className="w-3.5 h-3.5" />
              Preview
            </button>
            <button
              onClick={() => setActivePanel('console')}
              data-testid="console-tab"
              className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm transition ${
                activePanel === 'console' ? 'bg-zinc-800 text-white' : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              <Terminal className="w-3.5 h-3.5" />
              Console
            </button>
            <button
              onClick={() => setActivePanel('history')}
              data-testid="history-tab"
              className={`flex items-center gap-2 px-3 py-1.5 rounded text-sm transition ${
                activePanel === 'history' ? 'bg-zinc-800 text-white' : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              <History className="w-3.5 h-3.5" />
              History
            </button>
            
            <div className="ml-auto">
              <button
                onClick={() => setIsFullscreen(!isFullscreen)}
                className="p-1.5 text-zinc-500 hover:text-white transition"
              >
                {isFullscreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Panel Content */}
          <div className="flex-1 overflow-hidden">
            {activePanel === 'preview' && (
              <SandpackProvider
                template="react"
                files={files}
                theme="dark"
                options={{
                  externalResources: ['https://cdn.tailwindcss.com'],
                }}
              >
                <SandpackPreview
                  showNavigator={false}
                  showRefreshButton={true}
                  style={{ height: '100%' }}
                />
              </SandpackProvider>
            )}
            
            {activePanel === 'console' && (
              <ConsolePanel logs={logs} />
            )}
            
            {activePanel === 'history' && (
              <VersionHistory 
                versions={versions} 
                onRestore={restoreVersion}
                currentVersion={currentVersion}
              />
            )}
          </div>
        </div>
      </div>

      {/* Bottom Chat Panel */}
      <div className="border-t border-zinc-800 p-4 flex-shrink-0">
        {isBuilding && (
          <div className="mb-3">
            <div className="h-1 bg-zinc-800 rounded-full overflow-hidden">
              <motion.div 
                className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                initial={{ width: 0 }}
                animate={{ width: `${buildProgress}%` }}
              />
            </div>
          </div>
        )}

        {messages.length > 0 && (
          <div className="max-h-32 overflow-y-auto mb-3 space-y-2">
            {messages.slice(-4).map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] px-3 py-2 rounded-lg text-sm ${
                  msg.role === 'user' 
                    ? 'bg-zinc-700 text-white' 
                    : msg.error 
                      ? 'bg-red-500/10 text-red-400'
                      : 'bg-zinc-800 text-zinc-300'
                }`}>
                  {msg.isBuilding ? (
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 border-2 border-zinc-500 border-t-white rounded-full animate-spin" />
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

        {attachedFiles.length > 0 && (
          <div className="flex gap-2 mb-3 flex-wrap">
            {attachedFiles.map((file, i) => (
              <div key={i} className="flex items-center gap-2 px-3 py-1.5 bg-zinc-800 rounded-lg text-sm">
                {file.type.startsWith('image/') ? (
                  <Image className="w-4 h-4 text-blue-400" />
                ) : (
                  <FileText className="w-4 h-4 text-green-400" />
                )}
                <span className="text-zinc-300 max-w-[150px] truncate">{file.name}</span>
                <button onClick={() => removeFile(i)} className="text-zinc-500 hover:text-white">
                  <X className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex gap-3">
          <div className="flex-1 flex items-center gap-2 px-4 py-3 bg-zinc-800/50 rounded-xl">
            <button
              type="button"
              onClick={isRecording ? stopRecording : startRecording}
              data-testid="voice-input-button"
              className={`p-1.5 rounded-lg transition ${
                isRecording ? 'bg-red-500/20 text-red-400' : 'text-zinc-500 hover:text-white hover:bg-zinc-700'
              }`}
              title={isRecording ? 'Stop recording' : 'Voice input'}
            >
              {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>
            
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              data-testid="file-attach-button"
              className="p-1.5 rounded-lg text-zinc-500 hover:text-white hover:bg-zinc-700 transition"
              title="Attach file"
            >
              <Paperclip className="w-4 h-4" />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/*,.pdf,.txt,.md"
              onChange={handleFileSelect}
              className="hidden"
            />
            
            <div className="h-4 w-px bg-zinc-700" />
            
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              data-testid="chat-input"
              placeholder={versions.length > 0 ? "Describe changes..." : "Describe what you want to build..."}
              className="flex-1 bg-transparent text-white placeholder-zinc-500 outline-none text-sm"
              disabled={isBuilding}
            />
          </div>
          
          <button
            type="submit"
            disabled={!input.trim() || isBuilding}
            data-testid="submit-button"
            className="px-5 py-3 bg-white text-black rounded-xl text-sm font-medium disabled:opacity-30 disabled:cursor-not-allowed hover:bg-zinc-200 transition flex items-center gap-2"
          >
            {isBuilding ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>{versions.length > 0 ? 'Update' : 'Build'}</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Workspace;
