import { useEffect, useRef, useCallback } from 'react';
import { useGraphStore } from '@/store/graphStore';

const WS_BASE = `ws://${window.location.hostname}:8000`;

export function useGraphWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const { addNodeFromEvent, updateNodeResult } = useGraphStore();

  useEffect(() => {
    const ws = new WebSocket(`${WS_BASE}/ws/graph`);
    wsRef.current = ws;

    ws.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);
        if (msg.event === 'node_placed') {
          addNodeFromEvent(msg);
        } else if (msg.event === 'node_connected') {
          // Edge added from server
          const { source_id, target_id } = msg;
          useGraphStore.getState().onConnect({
            source: source_id,
            target: target_id,
            sourceHandle: null,
            targetHandle: null,
          } as any);
        } else if (msg.event === 'node_result') {
          updateNodeResult(msg.node_id, msg.summary, msg.artifact_type, msg.artifact_b64);
        }
      } catch (e) {
        console.warn('WS parse error:', e);
      }
    };

    ws.onerror = (e) => console.warn('Graph WS error:', e);
    ws.onclose = () => console.info('Graph WS closed');

    return () => ws.close();
  }, []);

  return wsRef;
}

export function useAgentWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const { addAgentMessage } = useGraphStore();

  useEffect(() => {
    const ws = new WebSocket(`${WS_BASE}/ws/agent`);
    wsRef.current = ws;

    ws.onmessage = (evt) => {
      try {
        const msg = JSON.parse(evt.data);
        addAgentMessage(msg);
      } catch (e) {
        console.warn('Agent WS parse error:', e);
      }
    };

    ws.onerror = (e) => console.warn('Agent WS error:', e);
    ws.onclose = () => console.info('Agent WS closed');

    return () => ws.close();
  }, []);

  const sendAgentCommand = useCallback((action: string, payload: Record<string, any>) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action, ...payload }));
    }
  }, []);

  return { wsRef, sendAgentCommand };
}
