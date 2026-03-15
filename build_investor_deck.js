const pptxgen = require('pptxgenjs');

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE';
pptx.author = 'Perplexity Computer';
pptx.company = 'SonAI';
pptx.subject = 'SonAI investor pitch deck';
pptx.title = 'SonAI investor deck';
pptx.lang = 'en-GB';
pptx.theme = {
  headFontFace: 'Trebuchet MS',
  bodyFontFace: 'Calibri',
  lang: 'en-GB'
};

const C = {
  bg: 'F7F6F2',
  surface: 'FBFBF9',
  border: 'D4D1CA',
  text: '28251D',
  muted: '7A7974',
  faint: 'BAB9B4',
  accent: '01696F',
  accentDark: '0C4E54',
  darkBg: '171614',
  darkSurface: '1C1B19',
  darkText: 'CDCCCA',
  teal2: '20808D',
  rust: 'A84B2F',
  gold: 'D19900'
};

function addSlideBase(slide, dark = false, slideNumber = null) {
  slide.background = { color: dark ? C.darkBg : C.bg };
  slide.addText('SonAI', {
    x: 0.45, y: 0.18, w: 1.2, h: 0.25,
    fontFace: 'Trebuchet MS', fontSize: 11.5,
    bold: true, color: dark ? 'F2EFEB' : C.accent,
    margin: 0
  });
  if (slideNumber !== null) {
    slide.addText(String(slideNumber), {
      x: 12.55, y: 7.0, w: 0.2, h: 0.18,
      fontFace: 'Calibri', fontSize: 8.5,
      color: dark ? 'A7A39B' : C.muted,
      margin: 0,
      align: 'right'
    });
  }
}

function addTitle(slide, title, subtitle = '', dark = false, opts = {}) {
  const titleY = opts.titleY ?? 0.65;
  const titleW = opts.titleW ?? 9.15;
  const titleH = opts.titleH ?? 0.95;
  const subtitleY = opts.subtitleY ?? 1.48;
  const subtitleW = opts.subtitleW ?? 9.5;
  const subtitleH = opts.subtitleH ?? 0.48;
  const titleSize = opts.titleSize ?? 26;
  const subtitleSize = opts.subtitleSize ?? 12.5;
  slide.addText(title, {
    x: 0.55, y: titleY, w: titleW, h: titleH,
    fontFace: 'Trebuchet MS', bold: true, fontSize: titleSize,
    color: dark ? 'FFFFFF' : C.text,
    margin: 0,
    fit: 'shrink'
  });
  if (subtitle) {
    slide.addText(subtitle, {
      x: 0.55, y: subtitleY, w: subtitleW, h: subtitleH,
      fontFace: 'Calibri', fontSize: subtitleSize,
      color: dark ? 'D6D1C8' : '686660',
      margin: 0,
      fit: 'shrink'
    });
  }
}

function addFooter(slide, textRuns, dark = false) {
  slide.addText(textRuns, {
    x: 0.55, y: 7.02, w: 12.0, h: 0.22,
    fontFace: 'Calibri', fontSize: 8.5,
    color: dark ? 'A7A39B' : C.muted,
    margin: 0,
    valign: 'mid'
  });
}

function addBulletList(slide, items, opts = {}) {
  const x = opts.x ?? 0.8;
  const y = opts.y ?? 1.9;
  const w = opts.w ?? 5.4;
  const h = opts.h ?? 3.7;
  const color = opts.color ?? C.text;
  const fontSize = opts.fontSize ?? 18;
  const runs = [];
  items.forEach((item, idx) => {
    runs.push({ text: item, options: { bullet: { indent: 12 }, hanging: 3 } });
    if (idx < items.length - 1) runs.push({ text: '\n' });
  });
  slide.addText(runs, {
    x, y, w, h,
    fontFace: 'Calibri', fontSize,
    color,
    breakLine: false,
    paraSpaceAfterPt: 12,
    valign: 'top',
    margin: 0.03
  });
}

// Slide 1
{
  const slide = pptx.addSlide();
  addSlideBase(slide, true, 1);
  slide.addShape(pptx.ShapeType.rect, {
    x: 0.55, y: 1.22, w: 5.7, h: 5.12,
    fill: { color: '211F1C' }, line: { color: '3A3732', pt: 1.1 }
  });
  slide.addText('AI-native audio intelligence for analysis and generation', {
    x: 0.78, y: 1.72, w: 5.0, h: 1.65,
    fontFace: 'Trebuchet MS', bold: true, fontSize: 28,
    color: 'FFFFFF', margin: 0
  });
  slide.addText('A natural-language node editor that turns reference audio into structured analysis, interpretable musical insight, and non-vocal flow-state output.', {
    x: 0.8, y: 3.82, w: 4.85, h: 1.1,
    fontFace: 'Calibri', fontSize: 16,
    color: 'D9D6D0', margin: 0
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 6.55, y: 1.28, w: 6.2, h: 4.9, rectRadius: 0.08,
    fill: { color: '1F2F31' }, line: { color: '355155', pt: 1 }
  });
  const cards = [
    ['Input', 'Drop an audio file and state an objective in plain English.'],
    ['Analysis', 'The agent places and runs spectral, temporal, pitch, onset, and segmentation nodes.'],
    ['Generation', 'SonAI assembles a soundscape graph and renders a new instrumental output.']
  ];
  cards.forEach((c, i) => {
    const y = 1.72 + i * 1.34;
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 6.95, y, w: 5.4, h: 1.08, rectRadius: 0.06,
      fill: { color: i === 0 ? C.accentDark : '27383A' },
      line: { color: i === 0 ? '4F98A3' : '3A5053', pt: 1 }
    });
    slide.addText(c[0], {
      x: 7.18, y: y + 0.12, w: 1.2, h: 0.2,
      fontFace: 'Trebuchet MS', fontSize: 13, bold: true,
      color: 'FFFFFF', margin: 0
    });
    slide.addText(c[1], {
      x: 7.18, y: y + 0.35, w: 4.75, h: 0.48,
      fontFace: 'Calibri', fontSize: 11.5,
      color: 'E2E0DB', margin: 0
    });
  });
  slide.addText('Investor deck • 5-slide overview', {
    x: 0.78, y: 6.83, w: 3.1, h: 0.24,
    fontFace: 'Calibri', fontSize: 10.5,
    color: 'B9B4AA', margin: 0
  });
}

// Slide 2
{
  const slide = pptx.addSlide();
  addSlideBase(slide, false, 2);
  addTitle(slide, 'The workflow gap in modern audio creation', 'Audio teams still move between disconnected tools for listening, analysis, interpretation, and generation.', false, { subtitleY: 1.5, subtitleW: 9.8 });
  [
    { text: 'Reference audio analysis is fragmented across scripts, plugins, notebooks, and DAWs.', y: 1.95, h: 0.58 },
    { text: 'Generative audio tools produce output quickly, but give little structural control over why a result sounds the way it does.', y: 2.82, h: 0.72 },
    { text: 'Teams lack a shared canvas that connects musical evidence to generation decisions in a reproducible workflow.', y: 4.02, h: 0.68 }
  ].forEach(item => {
    slide.addText(item.text, {
      x: 0.75, y: item.y, w: 5.95, h: item.h,
      fontFace: 'Calibri', fontSize: 17.5, color: C.text, margin: 0
    });
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 7.0, y: 1.82, w: 5.45, h: 4.25, rectRadius: 0.05,
    fill: { color: C.surface }, line: { color: C.border, pt: 1 }
  });
  const labels = [
    ['Listen', 'Reference track, stems, corpus'],
    ['Measure', 'Frequency, rhythm, pitch, segmentation'],
    ['Infer', 'Scene plan and role mapping'],
    ['Generate', 'Texture, instrument, granular, render']
  ];
  labels.forEach((c, i) => {
    const y = 2.1 + i * 0.84;
    slide.addShape(pptx.ShapeType.roundRect, {
      x: 7.3, y, w: 1.15, h: 0.38, rectRadius: 0.04,
      fill: { color: i === 0 ? 'E8F3F2' : 'F0EEEA' }, line: { color: C.border, pt: 0.75 }
    });
    slide.addText(c[0], {
      x: 7.48, y: y + 0.09, w: 0.8, h: 0.14,
      fontFace: 'Trebuchet MS', fontSize: 10.5, bold: true, color: C.text, margin: 0, align: 'center'
    });
    slide.addText(c[1], {
      x: 8.7, y: y + 0.03, w: 3.15, h: 0.3,
      fontFace: 'Calibri', fontSize: 12, color: C.text, margin: 0
    });
    if (i < labels.length - 1) {
      slide.addShape(pptx.ShapeType.line, {
        x: 9.72, y: y + 0.56, w: 0.18, h: 0,
        line: { color: C.accent, pt: 1.35, beginArrowType: 'none', endArrowType: 'triangle' }
      });
    }
  });
  slide.addText('SonAI turns this into one agent-driven canvas instead of four disconnected steps.', {
    x: 7.3, y: 5.38, w: 4.55, h: 0.5,
    fontFace: 'Calibri', fontSize: 12.6, bold: true, color: C.accentDark, margin: 0,
    fit: 'shrink'
  });
}

// Slide 3
{
  const slide = pptx.addSlide();
  addSlideBase(slide, false, 3);
  addTitle(slide, 'Product: a natural-language node editor for audio intelligence', 'The user provides a file and an objective. The agent constructs the graph, explains each step, and renders output.', false, { titleW: 9.55, titleH: 0.92, titleSize: 24, subtitleY: 1.48, subtitleW: 10.0 });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.75, y: 2.05, w: 12.0, h: 3.35, rectRadius: 0.05,
    fill: { color: C.surface }, line: { color: C.border, pt: 1 }
  });
  const cols = [
    ['Source + Transform', ['Load audio', 'Preprocess', 'STFT', 'HPSS']],
    ['Measure + Infer', ['Spectral stats', 'Temporal stats', 'Pitch / tonal', 'Segmentation + scene plan']],
    ['Compose + Render', ['Binaural layer', 'Texture layer', 'Instrument layer', 'Mix render']]
  ];
  cols.forEach((col, i) => {
    const x = 1.05 + i * 3.95;
    slide.addText(col[0], {
      x, y: 2.28, w: 3.2, h: 0.3,
      fontFace: 'Trebuchet MS', fontSize: 15, bold: true, color: C.text, margin: 0
    });
    col[1].forEach((item, j) => {
      slide.addShape(pptx.ShapeType.roundRect, {
        x, y: 2.72 + j * 0.6, w: 3.1, h: 0.4, rectRadius: 0.04,
        fill: { color: j === 0 ? 'E8F3F2' : 'F7F4EF' }, line: { color: C.border, pt: 0.75 }
      });
      slide.addText(item, {
        x: x + 0.14, y: 2.83 + j * 0.6, w: 2.8, h: 0.14,
        fontFace: 'Calibri', fontSize: 11.5, color: C.text, margin: 0
      });
    });
  });
  slide.addShape(pptx.ShapeType.line, { x: 4.68, y: 3.25, w: 0.38, h: 0, line: { color: C.accent, pt: 1.75, beginArrowType: 'none', endArrowType: 'triangle' } });
  slide.addShape(pptx.ShapeType.line, { x: 8.63, y: 3.25, w: 0.38, h: 0, line: { color: C.accent, pt: 1.75, beginArrowType: 'none', endArrowType: 'triangle' } });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.9, y: 5.86, w: 11.6, h: 0.72, rectRadius: 0.03,
    fill: { color: 'F5F2EC' }, line: { color: C.border, pt: 0.75 }
  });
  slide.addText('Differentiation', {
    x: 1.12, y: 6.1, w: 1.55, h: 0.18,
    fontFace: 'Trebuchet MS', fontSize: 13, bold: true, color: C.accentDark, margin: 0
  });
  slide.addText('Interpretable graph state, reusable node outputs, and no-vocals-by-design generation make SonAI more controllable than black-box prompt tools.', {
    x: 2.75, y: 6.02, w: 9.15, h: 0.34,
    fontFace: 'Calibri', fontSize: 12.8, color: C.text, margin: 0,
    fit: 'shrink'
  });
}

// Slide 4
{
  const slide = pptx.addSlide();
  addSlideBase(slide, false, 4);
  addTitle(slide, 'Validated demo: analysis to output in one graph', 'A live run on an uploaded reference track completed the analysis chain, generated a scene plan, and rendered a new WAV file.', false, { subtitleY: 1.5, subtitleW: 9.7 });
  slide.addImage({ path: '/home/user/workspace/step-5-complete-graph.png', x: 0.7, y: 1.95, w: 6.95, h: 4.15 });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 7.75, y: 1.95, w: 4.85, h: 4.15, rectRadius: 0.05,
    fill: { color: C.surface }, line: { color: C.border, pt: 1 }
  });
  slide.addText('Observed output', {
    x: 7.9, y: 2.05, w: 1.9, h: 0.2,
    fontFace: 'Trebuchet MS', fontSize: 15, bold: true, color: C.text, margin: 0
  });
  [
    'Input track loaded as 325.4s mono audio at 22050 Hz.',
    'Frequency analysis surfaced a spectral centroid around 881 Hz and a dominant pitch near 110.6 Hz in A major.',
    'The agent completed the graph through MixRender and wrote a real WAV output to disk.'
  ].forEach((line, i) => {
    slide.addText(line, {
      x: 7.95, y: 2.48 + i * 0.98, w: 4.15, h: 0.62,
      fontFace: 'Calibri', fontSize: 14, color: C.text, margin: 0
    });
  });
  slide.addText('Current state', {
    x: 7.95, y: 5.22, w: 1.7, h: 0.18,
    fontFace: 'Trebuchet MS', fontSize: 13.5, bold: true, color: C.accentDark, margin: 0
  });
  slide.addText('MVP stack is live with analysis tools, generation tools, agent orchestration, graph UI, and render output validation.', {
    x: 7.95, y: 5.5, w: 4.0, h: 0.4,
    fontFace: 'Calibri', fontSize: 12.6, color: C.text, margin: 0,
    fit: 'shrink'
  });
  addFooter(slide, [
    { text: 'Source: ' },
    { text: 'SonAI app', options: { hyperlink: { url: 'http://localhost:5173' } } },
    { text: ' · ' },
    { text: 'Backend health', options: { hyperlink: { url: 'http://127.0.0.1:8000/health' } } },
    { text: ' · ' },
    { text: 'Graph API', options: { hyperlink: { url: 'http://127.0.0.1:8000/api/graph/state' } } }
  ]);
}

// Slide 5
{
  const slide = pptx.addSlide();
  addSlideBase(slide, true, 5);
  addTitle(slide, 'Why SonAI can become the workflow layer for intelligent audio creation', 'The product starts as a power tool for creators and audio R&D teams, then expands into programmable analysis and generation infrastructure.', true, { titleW: 10.1, titleH: 0.92, titleSize: 24, subtitleY: 1.5, subtitleW: 10.5, subtitleH: 0.42, subtitleSize: 12.2 });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.75, y: 2.15, w: 3.75, h: 3.45, rectRadius: 0.05,
    fill: { color: '1E2627' }, line: { color: '344647', pt: 1 }
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 4.85, y: 2.15, w: 3.75, h: 3.45, rectRadius: 0.05,
    fill: { color: '1E2627' }, line: { color: '344647', pt: 1 }
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 8.95, y: 2.15, w: 3.75, h: 3.45, rectRadius: 0.05,
    fill: { color: '1E2627' }, line: { color: '344647', pt: 1 }
  });
  const endgame = [
    ['Wedge', 'Reference-audio analysis, flow-state generation, and reusable node workflows for creators and wellness audio teams.'],
    ['Expansion', 'API and MCP-native tooling for creative software, agents, and internal audio intelligence pipelines.'],
    ['Investor thesis', 'Own the interface between understanding sound and generating controlled audio output.']
  ];
  endgame.forEach((c, i) => {
    const x = 1.0 + i * 4.1;
    slide.addText(c[0], {
      x, y: 2.42, w: 2.55, h: 0.24,
      fontFace: 'Trebuchet MS', fontSize: 16, bold: true, color: 'FFFFFF', margin: 0
    });
    slide.addText(c[1], {
      x, y: 3.12, w: 3.08, h: 1.12,
      fontFace: 'Calibri', fontSize: 14.1, color: 'D8D5CF', margin: 0
    });
  });
  slide.addShape(pptx.ShapeType.roundRect, {
    x: 0.95, y: 5.98, w: 11.55, h: 0.72, rectRadius: 0.03,
    fill: { color: '202927' }, line: { color: '344647', pt: 0.75 }
  });
  slide.addText('Next conversation', {
    x: 1.15, y: 6.2, w: 1.9, h: 0.16,
    fontFace: 'Trebuchet MS', fontSize: 13, bold: true, color: 'FFFFFF', margin: 0
  });
  slide.addText('Refine this into a raise-ready version with market sizing, go-to-market milestones, and a funding ask tailored to your stage.', {
    x: 3.15, y: 6.1, w: 8.65, h: 0.32,
    fontFace: 'Calibri', fontSize: 12.6, color: 'D8D5CF', margin: 0,
    fit: 'shrink'
  });
}

pptx.writeFile({ fileName: '/home/user/workspace/sonai-investor-deck.pptx' });
