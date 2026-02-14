import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Plus, Zap, FolderOpen, Clock, CheckCircle, 
  AlertCircle, TrendingUp, Bot, ArrowRight, Play,
  Share2, Copy, Bookmark
} from 'lucide-react';
import { useAuth, API } from '../App';
import axios from 'axios';
import DeployButton from '../components/DeployButton';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

const Dashboard = () => {
  const { user, token } = useAuth();
  const [stats, setStats] = useState(null);
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionFeedback, setActionFeedback] = useState(null);

  const handleShare = async (e, projectId) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      const { data } = await axios.post(`${API}/share/create`, { project_id: projectId, read_only: true }, { headers: { Authorization: `Bearer ${token}` } });
      const url = `${window.location.origin}${data.share_url}`;
      await navigator.clipboard.writeText(url);
      setActionFeedback({ type: 'share', msg: 'Share link copied!' });
      setTimeout(() => setActionFeedback(null), 3000);
    } catch (err) {
      setActionFeedback({ type: 'error', msg: err.response?.data?.detail || 'Share failed' });
      setTimeout(() => setActionFeedback(null), 3000);
    }
  };

  const handleDuplicate = async (e, projectId) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      const { data } = await axios.post(`${API}/projects/${projectId}/duplicate`, {}, { headers: { Authorization: `Bearer ${token}` } });
      setProjects(prev => [data.project, ...prev.slice(0, 4)]);
      setActionFeedback({ type: 'duplicate', msg: 'Project duplicated!' });
      setTimeout(() => setActionFeedback(null), 3000);
    } catch (err) {
      setActionFeedback({ type: 'error', msg: err.response?.data?.detail || 'Duplicate failed' });
      setTimeout(() => setActionFeedback(null), 3000);
    }
  };

  const handleSaveAsTemplate = async (e, projectId) => {
    e.preventDefault();
    e.stopPropagation();
    const name = window.prompt('Template name:', 'My template');
    if (name == null) return;
    try {
      await axios.post(`${API}/projects/${projectId}/save-as-template`, { name: name || 'My template' }, { headers: { Authorization: `Bearer ${token}` } });
      setActionFeedback({ type: 'template', msg: 'Saved as template!' });
      setTimeout(() => setActionFeedback(null), 3000);
    } catch (err) {
      setActionFeedback({ type: 'error', msg: err.response?.data?.detail || 'Save failed' });
      setTimeout(() => setActionFeedback(null), 3000);
    }
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, projectsRes] = await Promise.all([
          axios.get(`${API}/dashboard/stats`, { headers: { Authorization: `Bearer ${token}` } }),
          axios.get(`${API}/projects`, { headers: { Authorization: `Bearer ${token}` } })
        ]);
        setStats(statsRes.data);
        setProjects(projectsRes.data.projects.slice(0, 5));
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [token]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const statCards = [
    { label: 'Token Balance', value: stats?.token_balance?.toLocaleString() || 0, icon: Zap, color: 'blue', trend: '+5%' },
    { label: 'Total Projects', value: stats?.total_projects || 0, icon: FolderOpen, color: 'purple', trend: '+12%' },
    { label: 'Completed', value: stats?.completed_projects || 0, icon: CheckCircle, color: 'green', trend: '+8%' },
    { label: 'Running', value: stats?.running_projects || 0, icon: Clock, color: 'orange', trend: null }
  ];

  return (
    <div className="space-y-8 bg-[#FAF9F7] min-h-full" data-testid="dashboard">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold mb-2 text-gray-900">Welcome back, {user?.name?.split(' ')[0]}!</h1>
          <p className="text-gray-600">Here's what's happening with your projects.</p>
        </div>
        <Link
          to="/app/projects/new"
          className="inline-flex items-center gap-2 px-6 py-3 bg-blue-500 hover:bg-blue-600 rounded-lg font-medium transition neon-blue"
          data-testid="new-project-btn"
        >
          <Plus className="w-5 h-5" />
          New Project
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat, i) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className={`p-6 bg-white rounded-xl border border-gray-200 hover:border-${stat.color}-500/40 transition-all group shadow-sm`}
            data-testid={`stat-${stat.label.toLowerCase().replace(' ', '-')}`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className={`w-12 h-12 bg-${stat.color}-500/10 rounded-lg flex items-center justify-center group-hover:bg-${stat.color}-500/20 transition`}>
                <stat.icon className={`w-6 h-6 text-${stat.color}-400`} />
              </div>
              {stat.trend && (
                <span className="flex items-center gap-1 text-sm text-green-400">
                  <TrendingUp className="w-4 h-4" />
                  {stat.trend}
                </span>
              )}
            </div>
            <p className="text-3xl font-bold mb-1">{stat.value}</p>
            <p className="text-gray-500 text-sm">{stat.label}</p>
          </motion.div>
        ))}
      </div>

      {/* Charts & Activity */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Usage Chart */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="lg:col-span-2 p-6 bg-white rounded-xl border border-gray-200 shadow-sm"
        >
          <h3 className="text-lg font-semibold mb-6 text-gray-900">Weekly Token Usage</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats?.weekly_data || []}>
                <defs>
                  <linearGradient id="tokenGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: '#6B7280', fontSize: 12 }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#6B7280', fontSize: 12 }} tickFormatter={(v) => `${(v/1000).toFixed(0)}K`} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  labelStyle={{ color: '#fff' }}
                  formatter={(value) => [`${value.toLocaleString()} tokens`, 'Usage']}
                />
                <Area type="monotone" dataKey="tokens" stroke="#3B82F6" strokeWidth={2} fill="url(#tokenGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="p-6 bg-white rounded-xl border border-gray-200 shadow-sm"
        >
          <h3 className="text-lg font-semibold mb-6 text-gray-900">Quick Actions</h3>
          <div className="space-y-3">
            {[
              { label: 'Create Website', icon: Plus, href: '/app/projects/new?type=website' },
              { label: 'Create API', icon: Bot, href: '/app/projects/new?type=api' },
              { label: 'Buy Tokens', icon: Zap, href: '/app/tokens' },
              { label: 'View Patterns', icon: FolderOpen, href: '/app/patterns' }
            ].map(action => (
              <Link
                key={action.label}
                to={action.href}
                className="flex items-center gap-3 p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition group"
              >
                <action.icon className="w-5 h-5 text-gray-500 group-hover:text-blue-600" />
                <span className="flex-1">{action.label}</span>
                <ArrowRight className="w-4 h-4 text-gray-500 group-hover:text-blue-600 transition" />
              </Link>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Recent Projects */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="p-6 bg-[#0a0a0a] rounded-xl border border-white/10"
      >
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold">Recent Projects</h3>
          <Link to="/app" className="text-sm text-blue-400 hover:text-blue-300">View all</Link>
        </div>
        
        {projects.length === 0 ? (
          <div className="text-center py-12">
            <FolderOpen className="w-12 h-12 text-gray-600 mx-auto mb-4" />
            <p className="text-gray-400 mb-4">No projects yet</p>
            <Link
              to="/app/projects/new"
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500 hover:bg-blue-600 rounded-lg font-medium transition"
            >
              <Plus className="w-4 h-4" />
              Create your first project
            </Link>
          </div>
        ) : (
          <>
            {actionFeedback && (
              <div className={`mb-4 px-4 py-2 rounded-lg text-sm ${actionFeedback.type === 'error' ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                {actionFeedback.msg}
              </div>
            )}
            <div className="space-y-4">
            {projects.map(project => (
              <div
                key={project.id}
                className="flex items-center gap-4 p-4 bg-gray-50 hover:bg-gray-100 rounded-lg transition group"
                data-testid={`project-${project.id}`}
              >
                <Link to={`/app/projects/${project.id}`} className="flex items-center gap-4 flex-1 min-w-0">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${
                    project.status === 'completed' ? 'bg-green-500/20' :
                    project.status === 'running' ? 'bg-blue-500/20 animate-pulse' :
                    project.status === 'failed' ? 'bg-red-500/20' :
                    'bg-gray-500/20'
                  }`}>
                    {project.status === 'completed' ? <CheckCircle className="w-5 h-5 text-green-400" /> :
                     project.status === 'running' ? <Play className="w-5 h-5 text-blue-400" /> :
                     project.status === 'failed' ? <AlertCircle className="w-5 h-5 text-red-400" /> :
                     <Clock className="w-5 h-5 text-gray-400" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{project.name}</p>
                    <p className="text-sm text-gray-500">{project.project_type} • {project.tokens_used?.toLocaleString()} tokens used</p>
                  </div>
                  <div className="text-right shrink-0 flex items-center gap-2">
                    {project.status === 'completed' && project.quality_score?.overall_score != null && (
                      <span className="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-700 text-slate-200 text-xs font-medium" title="Code quality score">
                        <span className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold bg-emerald-500/30 text-emerald-300">{Math.round(project.quality_score.overall_score)}</span>
                        Quality
                      </span>
                    )}
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      project.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                      project.status === 'running' ? 'bg-blue-500/20 text-blue-400' :
                      project.status === 'failed' ? 'bg-red-500/20 text-red-400' :
                      'bg-gray-500/20 text-gray-400'
                    }`}>
                      {project.status}
                    </span>
                  </div>
                </Link>
                <div className="flex items-center gap-1 shrink-0" onClick={e => e.preventDefault()}>
                  {project.status === 'completed' && (
                    <DeployButton projectId={project.id} variant="icon" onFeedback={(fb) => { setActionFeedback(fb); setTimeout(() => setActionFeedback(null), fb.type === 'error' ? 4000 : 3000); }} />
                  )}
                  <button type="button" onClick={(e) => handleShare(e, project.id)} className="p-2 text-gray-500 hover:text-blue-600 hover:bg-blue-500/10 rounded-lg" title="Share"> <Share2 className="w-4 h-4" /> </button>
                  <button type="button" onClick={(e) => handleDuplicate(e, project.id)} className="p-2 text-gray-500 hover:text-green-600 hover:bg-green-500/10 rounded-lg" title="Duplicate"> <Copy className="w-4 h-4" /> </button>
                  <button type="button" onClick={(e) => handleSaveAsTemplate(e, project.id)} className="p-2 text-gray-500 hover:text-purple-600 hover:bg-purple-500/10 rounded-lg" title="Save as template"> <Bookmark className="w-4 h-4" /> </button>
                </div>
              </div>
            ))}
            </div>
          </>
        )}
      </motion.div>
    </div>
  );
};

export default Dashboard;