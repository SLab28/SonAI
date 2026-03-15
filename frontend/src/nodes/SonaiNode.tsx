import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';

interface SonaiNodeData {
  nodeType: string;
  params: Record<string, any>;
  reasoning: string;
  summary: string;
  artifactType: string;
  artifactB64: string | null;
  color: string;
  category: string;
  [key: string]: unknown;
}

function SonaiNode({ data }: { data: SonaiNodeData }) {
  const { nodeType, summary, artifactType, artifactB64, color, category } = data;

  return (
    <div
      className="rounded-lg shadow-md bg-white border border-gray-200 min-w-[200px] max-w-[260px] overflow-hidden"
      data-testid={`node-${nodeType}`}
    >
      {/* Header */}
      <div
        className="px-3 py-1.5 text-white text-xs font-semibold tracking-wide uppercase flex items-center justify-between"
        style={{ backgroundColor: color }}
      >
        <span>{nodeType}</span>
        <span className="text-[10px] opacity-80 font-normal">{category}</span>
      </div>

      {/* Body */}
      <div className="p-3">
        {/* Summary */}
        {summary ? (
          <p className="text-xs text-gray-700 leading-relaxed" data-testid={`summary-${nodeType}`}>
            {summary}
          </p>
        ) : (
          <p className="text-xs text-gray-400 italic">Running…</p>
        )}

        {/* Artifact preview */}
        {artifactType === 'image/png' && artifactB64 && (
          <img
            src={`data:image/png;base64,${artifactB64}`}
            alt={`${nodeType} artifact`}
            className="mt-2 rounded border border-gray-100 w-full"
            data-testid={`artifact-${nodeType}`}
          />
        )}
      </div>

      {/* Handles */}
      <Handle type="target" position={Position.Left} className="!bg-gray-400 !w-2 !h-2" />
      <Handle type="source" position={Position.Right} className="!bg-gray-400 !w-2 !h-2" />
    </div>
  );
}

export default memo(SonaiNode);
