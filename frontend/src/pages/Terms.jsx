import { Link } from 'react-router-dom';

export default function Terms() {
  return (
    <div className="max-w-3xl mx-auto p-6 text-gray-800">
      <h1 className="text-2xl font-bold mb-4">Terms of Use</h1>
      <p className="text-sm text-gray-500 mb-6">Last updated: 2026</p>
      <div className="prose prose-sm space-y-4">
        <p>By using CrucibAI you agree to these terms.</p>
        <h2 className="text-lg font-semibold mt-6">Use of service</h2>
        <p>You may use the service for building applications with AI assistance. You are responsible for your API keys and for the content you generate.</p>
        <h2 className="text-lg font-semibold mt-6">Token usage</h2>
        <p>Token consumption is metered and may be subject to the plan you choose. Unused tokens do not expire unless otherwise stated.</p>
        <h2 className="text-lg font-semibold mt-6">Acceptable use</h2>
        <p>Do not use the service for illegal content, to harm others, or to circumvent security. We may suspend accounts that violate these terms.</p>
        <h2 className="text-lg font-semibold mt-6">Changes</h2>
        <p>We may update these terms; continued use after changes constitutes acceptance.</p>
      </div>
      <Link to="/" className="inline-block mt-8 text-blue-600 hover:text-blue-700">← Back</Link>
    </div>
  );
}
