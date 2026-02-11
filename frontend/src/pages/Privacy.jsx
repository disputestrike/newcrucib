import { Link } from 'react-router-dom';

export default function Privacy() {
  return (
    <div className="max-w-3xl mx-auto p-6 text-gray-800">
      <h1 className="text-2xl font-bold mb-4">Privacy Policy</h1>
      <p className="text-sm text-gray-500 mb-6">Last updated: 2026</p>
      <div className="prose prose-sm space-y-4">
        <p>CrucibAI respects your privacy. We collect only what is needed to provide the service.</p>
        <h2 className="text-lg font-semibold mt-6">Data we collect</h2>
        <p>Account data (email, name), project and build data you create, and usage metrics (e.g. token consumption) to operate the platform and billing.</p>
        <h2 className="text-lg font-semibold mt-6">API keys</h2>
        <p>API keys you add in Settings are stored per-user and used only to call AI providers (OpenAI, Anthropic) for your builds. We do not share them with third parties.</p>
        <h2 className="text-lg font-semibold mt-6">Retention</h2>
        <p>We retain project and chat data for as long as your account is active. You may request deletion of your data by contacting support.</p>
        <h2 className="text-lg font-semibold mt-6">Contact</h2>
        <p>For privacy questions, contact us at the support address provided in the app.</p>
      </div>
      <Link to="/" className="inline-block mt-8 text-blue-600 hover:text-blue-700">← Back</Link>
    </div>
  );
}
