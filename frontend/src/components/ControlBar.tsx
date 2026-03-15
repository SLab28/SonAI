import { useState, useCallback } from 'react';

interface ControlBarProps {
  onRunAgent: (filePath: string, objective: string) => void;
}

export default function ControlBar({ onRunAgent }: ControlBarProps) {
  const [filePath, setFilePath] = useState('');
  const [objective, setObjective] = useState('Create a flow-state soundscape');

  const handleRun = useCallback(() => {
    if (!filePath.trim()) return;
    onRunAgent(filePath.trim(), objective.trim());
  }, [filePath, objective, onRunAgent]);

  return (
    <div className="h-12 bg-white border-b border-gray-200 flex items-center gap-3 px-4" data-testid="control-bar">
      {/* Logo */}
      <div className="flex items-center gap-2 mr-4">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" aria-label="SonAI logo">
          <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.5" />
          <path d="M8 15c0-3 2-6 4-6s4 3 4 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          <circle cx="12" cy="9" r="2" fill="currentColor" />
        </svg>
        <span className="font-semibold text-sm tracking-tight">SonAI</span>
      </div>

      {/* File path input */}
      <input
        type="text"
        placeholder="Audio file path…"
        value={filePath}
        onChange={(e) => setFilePath(e.target.value)}
        className="px-2 py-1 text-xs border border-gray-200 rounded bg-gray-50 w-48 focus:outline-none focus:border-gray-400"
        data-testid="input-file-path"
      />

      {/* Objective input */}
      <input
        type="text"
        placeholder="Objective…"
        value={objective}
        onChange={(e) => setObjective(e.target.value)}
        className="px-2 py-1 text-xs border border-gray-200 rounded bg-gray-50 flex-1 max-w-sm focus:outline-none focus:border-gray-400"
        data-testid="input-objective"
      />

      {/* Run button */}
      <button
        onClick={handleRun}
        disabled={!filePath.trim()}
        className="px-3 py-1 text-xs font-medium text-white bg-black rounded hover:bg-gray-800 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        data-testid="button-run-agent"
      >
        Run Agent
      </button>
    </div>
  );
}
