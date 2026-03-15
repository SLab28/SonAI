import { useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  ReactFlowProvider,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { useGraphStore, NODE_COLORS } from '@/store/graphStore';
import { useGraphWebSocket, useAgentWebSocket } from '@/ws/useWebSocket';
import SonaiNode from '@/nodes/SonaiNode';
import NodePalette from '@/components/NodePalette';
import AgentPanel from '@/components/AgentPanel';
import ControlBar from '@/components/ControlBar';

const nodeTypes = {
  sonaiNode: SonaiNode,
};

function FlowCanvas() {
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    addNodeFromEvent,
  } = useGraphStore();

  const graphWs = useGraphWebSocket();
  const { sendAgentCommand } = useAgentWebSocket();

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();
      const nodeType = event.dataTransfer.getData('nodeType');
      if (!nodeType) return;

      const bounds = (event.target as HTMLElement).closest('.react-flow')?.getBoundingClientRect();
      if (!bounds) return;

      const x = event.clientX - bounds.left;
      const y = event.clientY - bounds.top;

      // Place node via REST API
      fetch('/api/graph/place', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ node_type: nodeType, x, y, params: {} }),
      }).catch(console.error);
    },
    []
  );

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const handleRunAgent = useCallback(
    (filePath: string, objective: string) => {
      sendAgentCommand('run_agent', { file_path: filePath, objective });
    },
    [sendAgentCommand]
  );

  return (
    <div className="flex flex-col h-screen w-screen">
      <ControlBar onRunAgent={handleRunAgent} />
      <div className="flex flex-1 overflow-hidden">
        <NodePalette />
        <div className="flex-1 relative" data-testid="canvas">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            onDrop={onDrop}
            onDragOver={onDragOver}
            fitView
            proOptions={{ hideAttribution: true }}
          >
            <Background color="#e5e7eb" gap={20} size={1} />
            <Controls position="bottom-left" />
            <MiniMap
              nodeColor={(n) => (n.data as any)?.color || '#6b7280'}
              maskColor="rgba(255,255,255,0.7)"
              position="bottom-right"
            />
          </ReactFlow>
        </div>
        <AgentPanel />
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ReactFlowProvider>
      <FlowCanvas />
    </ReactFlowProvider>
  );
}
