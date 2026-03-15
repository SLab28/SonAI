import { create } from 'zustand';
import {
  Node,
  Edge,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
  OnNodesChange,
  OnEdgesChange,
  OnConnect,
  NodeChange,
  EdgeChange,
  Connection,
} from '@xyflow/react';

// Node category → header colour
export const NODE_COLORS: Record<string, string> = {
  LoadAudio: '#6b7280',
  Preprocess: '#6b7280',
  STFT: '#3b82f6',
  HPSS: '#3b82f6',
  SpectralStats: '#22c55e',
  TemporalStats: '#22c55e',
  Onsets: '#22c55e',
  PitchTonal: '#22c55e',
  MFCC: '#22c55e',
  Chroma: '#22c55e',
  SegmentMap: '#f59e0b',
  InsightComposer: '#f59e0b',
  BinauralBeatGen: '#a855f7',
  TextureLayer: '#a855f7',
  InstrumentLayer: '#a855f7',
  GranularCloud: '#a855f7',
  MixRender: '#ef4444',
};

export const NODE_CATEGORIES: Record<string, string> = {
  LoadAudio: 'Source',
  Preprocess: 'Source',
  STFT: 'Transform',
  HPSS: 'Transform',
  SpectralStats: 'Measure',
  TemporalStats: 'Measure',
  Onsets: 'Measure',
  PitchTonal: 'Measure',
  MFCC: 'Measure',
  Chroma: 'Measure',
  SegmentMap: 'Infer',
  InsightComposer: 'Infer',
  BinauralBeatGen: 'Compose',
  TextureLayer: 'Compose',
  InstrumentLayer: 'Compose',
  GranularCloud: 'Compose',
  MixRender: 'Render',
};

export interface AgentMessage {
  event: string;
  step?: string;
  reasoning?: string;
  message?: string;
  scene_plan?: any;
  results?: Record<string, string>;
}

interface GraphState {
  nodes: Node[];
  edges: Edge[];
  agentMessages: AgentMessage[];
  onNodesChange: OnNodesChange;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
  addNodeFromEvent: (event: any) => void;
  updateNodeResult: (nodeId: string, summary: string, artifactType?: string, artifactB64?: string) => void;
  addAgentMessage: (msg: AgentMessage) => void;
  clearGraph: () => void;
}

export const useGraphStore = create<GraphState>((set, get) => ({
  nodes: [],
  edges: [],
  agentMessages: [],

  onNodesChange: (changes: NodeChange[]) => {
    set({ nodes: applyNodeChanges(changes, get().nodes) as Node[] });
  },

  onEdgesChange: (changes: EdgeChange[]) => {
    set({ edges: applyEdgeChanges(changes, get().edges) });
  },

  onConnect: (connection: Connection) => {
    set({ edges: addEdge(connection, get().edges) });
  },

  addNodeFromEvent: (event: any) => {
    const newNode: Node = {
      id: event.node_id,
      type: 'sonaiNode',
      position: { x: event.x || 0, y: event.y || 0 },
      data: {
        nodeType: event.node_type,
        params: event.params || {},
        reasoning: event.reasoning || '',
        summary: '',
        artifactType: 'none',
        artifactB64: null,
        color: NODE_COLORS[event.node_type] || '#6b7280',
        category: NODE_CATEGORIES[event.node_type] || 'Unknown',
      },
    };
    set({ nodes: [...get().nodes, newNode] });
  },

  updateNodeResult: (nodeId, summary, artifactType, artifactB64) => {
    set({
      nodes: get().nodes.map((n) =>
        n.id === nodeId
          ? {
              ...n,
              data: {
                ...n.data,
                summary,
                artifactType: artifactType || 'none',
                artifactB64: artifactB64 || null,
              },
            }
          : n
      ),
    });
  },

  addAgentMessage: (msg) => {
    set({ agentMessages: [...get().agentMessages, msg] });
  },

  clearGraph: () => {
    set({ nodes: [], edges: [], agentMessages: [] });
  },
}));
