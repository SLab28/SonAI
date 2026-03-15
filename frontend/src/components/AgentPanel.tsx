import { useGraphStore } from '@/store/graphStore';

export default function AgentPanel() {
  const messages = useGraphStore((s) => s.agentMessages);

  return (
    <div className="w-72 bg-gray-50 border-l border-gray-200 overflow-y-auto flex flex-col" data-testid="agent-panel">
      <div className="p-3 border-b border-gray-200">
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
          Agent Activity
        </h2>
      </div>
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {messages.length === 0 && (
          <p className="text-xs text-gray-400 italic">
            No agent activity yet. Drop an audio file and set an objective to start.
          </p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`p-2 rounded text-xs leading-relaxed ${
              msg.event === 'approval_required'
                ? 'bg-amber-50 border border-amber-200 text-amber-800'
                : msg.event === 'agent_complete'
                ? 'bg-green-50 border border-green-200 text-green-800'
                : 'bg-white border border-gray-100 text-gray-700'
            }`}
            data-testid={`agent-msg-${i}`}
          >
            {msg.step && (
              <span className="font-semibold text-gray-900 mr-1">[{msg.step}]</span>
            )}
            {msg.reasoning || msg.message || JSON.stringify(msg)}
          </div>
        ))}
      </div>
    </div>
  );
}
