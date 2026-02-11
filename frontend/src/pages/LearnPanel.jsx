import { BookOpen, Code, Zap, Shield, Palette } from 'lucide-react';

const sections = [
  {
    icon: Code,
    title: 'Describe what you want',
    body: 'In the Workspace chat, describe your app in plain English. Use "Build a todo app" or "Create a dashboard with charts".',
  },
  {
    icon: Zap,
    title: 'Use @ and / in chat',
    body: 'Type @ to add context (e.g. @App.js). Type / for commands like /fix or /explain. The command palette (Ctrl+K) lists all actions.',
  },
  {
    icon: Palette,
    title: 'Templates and prompts',
    body: 'Use the Prompt Library and Templates to start from proven patterns. Save your own prompts for reuse.',
  },
  {
    icon: Shield,
    title: 'Security and quality',
    body: 'Use Auto-fix when you see errors. Run Security scan and Accessibility check from the workspace or API.',
  },
];

export default function LearnPanel() {
  return (
    <div className="min-h-screen bg-[#050505] text-white p-6">
      <div className="max-w-2xl mx-auto">
        <div className="flex items-center gap-3 mb-8">
          <div className="p-3 rounded-xl bg-blue-500/20">
            <BookOpen className="w-8 h-8 text-blue-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Learn CrucibAI</h1>
            <p className="text-zinc-400">Quick tips to build apps with AI</p>
          </div>
        </div>
        <div className="space-y-6">
          {sections.map(({ icon: Icon, title, body }) => (
            <div key={title} className="p-5 rounded-xl border border-zinc-800 bg-zinc-900/50">
              <div className="flex items-start gap-4">
                <div className="p-2 rounded-lg bg-zinc-800 shrink-0">
                  <Icon className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <h2 className="font-semibold mb-1">{title}</h2>
                  <p className="text-sm text-zinc-400">{body}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
