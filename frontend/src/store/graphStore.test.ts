import { describe, it, expect, beforeEach } from 'vitest';
import { useGraphStore } from './graphStore';

describe('graphStore', () => {
  beforeEach(() => {
    useGraphStore.getState().clearGraph();
  });

  it('starts with empty nodes and edges', () => {
    const state = useGraphStore.getState();
    expect(state.nodes).toHaveLength(0);
    expect(state.edges).toHaveLength(0);
  });

  it('adds a node from event', () => {
    useGraphStore.getState().addNodeFromEvent({
      node_id: 'test-1',
      node_type: 'LoadAudio',
      x: 100,
      y: 200,
      params: { file_path: 'test.wav' },
      reasoning: 'Loading audio',
    });
    const state = useGraphStore.getState();
    expect(state.nodes).toHaveLength(1);
    expect(state.nodes[0].id).toBe('test-1');
    expect(state.nodes[0].data.nodeType).toBe('LoadAudio');
    expect(state.nodes[0].data.color).toBe('#6b7280');
    expect(state.nodes[0].data.category).toBe('Source');
  });

  it('updates node result', () => {
    useGraphStore.getState().addNodeFromEvent({
      node_id: 'test-2',
      node_type: 'STFT',
      x: 0,
      y: 0,
    });
    useGraphStore.getState().updateNodeResult('test-2', 'STFT computed', 'image/png', 'abc123');
    const node = useGraphStore.getState().nodes[0];
    expect(node.data.summary).toBe('STFT computed');
    expect(node.data.artifactType).toBe('image/png');
    expect(node.data.artifactB64).toBe('abc123');
  });

  it('adds agent messages', () => {
    useGraphStore.getState().addAgentMessage({
      event: 'agent_reasoning',
      step: 'LoadAudio',
      reasoning: 'Loading file',
    });
    expect(useGraphStore.getState().agentMessages).toHaveLength(1);
    expect(useGraphStore.getState().agentMessages[0].step).toBe('LoadAudio');
  });

  it('clears graph', () => {
    useGraphStore.getState().addNodeFromEvent({
      node_id: 'n1',
      node_type: 'LoadAudio',
      x: 0,
      y: 0,
    });
    useGraphStore.getState().addAgentMessage({
      event: 'test',
    });
    useGraphStore.getState().clearGraph();
    expect(useGraphStore.getState().nodes).toHaveLength(0);
    expect(useGraphStore.getState().agentMessages).toHaveLength(0);
  });

  it('assigns correct colors to node types', () => {
    const types = ['STFT', 'SpectralStats', 'InsightComposer', 'BinauralBeatGen', 'MixRender'];
    const expectedColors = ['#3b82f6', '#22c55e', '#f59e0b', '#a855f7', '#ef4444'];
    types.forEach((t, i) => {
      useGraphStore.getState().addNodeFromEvent({
        node_id: `color-${i}`,
        node_type: t,
        x: 0,
        y: 0,
      });
    });
    const nodes = useGraphStore.getState().nodes;
    types.forEach((_, i) => {
      expect(nodes[i].data.color).toBe(expectedColors[i]);
    });
  });
});
