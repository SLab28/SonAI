import { NODE_COLORS, NODE_CATEGORIES } from '@/store/graphStore';

const PALETTE_SECTIONS = [
  {
    title: 'Source',
    nodes: ['LoadAudio', 'Preprocess'],
  },
  {
    title: 'Transform',
    nodes: ['STFT', 'HPSS'],
  },
  {
    title: 'Measure',
    nodes: ['SpectralStats', 'TemporalStats', 'Onsets', 'PitchTonal', 'MFCC', 'Chroma'],
  },
  {
    title: 'Infer',
    nodes: ['SegmentMap', 'InsightComposer'],
  },
  {
    title: 'Compose',
    nodes: ['BinauralBeatGen', 'TextureLayer', 'InstrumentLayer', 'GranularCloud'],
  },
  {
    title: 'Render',
    nodes: ['MixRender'],
  },
];

export default function NodePalette() {
  return (
    <div className="w-52 bg-gray-50 border-r border-gray-200 overflow-y-auto" data-testid="node-palette">
      <div className="p-3">
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">
          Node Palette
        </h2>
        {PALETTE_SECTIONS.map((section) => (
          <div key={section.title} className="mb-3">
            <h3 className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider mb-1">
              {section.title}
            </h3>
            {section.nodes.map((nodeType) => (
              <div
                key={nodeType}
                className="flex items-center gap-2 px-2 py-1 rounded text-xs text-gray-700 hover:bg-gray-100 cursor-grab"
                draggable
                onDragStart={(e) => {
                  e.dataTransfer.setData('nodeType', nodeType);
                }}
                data-testid={`palette-${nodeType}`}
              >
                <span
                  className="w-2 h-2 rounded-full flex-shrink-0"
                  style={{ backgroundColor: NODE_COLORS[nodeType] }}
                />
                <span className="truncate">{nodeType}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
