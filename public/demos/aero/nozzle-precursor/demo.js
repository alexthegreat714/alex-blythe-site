const root = '/demos/aero/nozzle-precursor';
document.documentElement.classList.add('js');

const explanationCopy = {
  validation: {
    title: 'Why isn’t this validated?',
    body: 'Numerical convergence shows that the discretized equations reached the declared numerical criteria. Validation requires comparison with an appropriate analytical, published, or experimental reference. This retained case has no such reference, so Aero leaves validation unestablished.',
  },
  residuals: {
    title: 'What does residual convergence mean?',
    body: 'The four required initial residuals at outer iteration 350 are each below 1 × 10⁻⁴. That supports convergence of the numerical iteration for this mesh and model. It does not show that the chosen equations, properties, boundaries, or geometry represent the intended physical system accurately.',
  },
  mesh: {
    title: 'Why did mesh independence fail?',
    body: 'The eligible coarse and medium cases passed their numerical gates, but maximum Mach changed by 5.71%, above the declared 2% comparison tolerance. The fine case completed 8,000 iterations but failed its residual gates, so it was ineligible for the comparison. Aero therefore does not claim mesh independence.',
  },
  next: {
    title: 'What would you do next?',
    body: 'First, recover a converged fine-mesh solution and repeat the multi-quantity comparison. Then define an appropriate validation reference and upgrade the model for the intended use. A choking study would require reviewed inlet and back-pressure conditions and appropriate compressible numerics—not a stronger label on this mass-flow-driven precursor.',
  },
  conservation: {
    title: 'Why check conservation separately?',
    body: 'Residuals measure how the iterative algebraic solution is settling. Conservation checks ask whether the resulting flow accounts for mass and energy within declared tolerances. A low residual can coexist with a physically unacceptable imbalance, so these are independent pieces of evidence.',
  },
  ready: {
    title: 'What would make this design-ready?',
    body: 'Design readiness would require a model-fidelity argument appropriate to the declared use, converged mesh-independence evidence, and agreement with an appropriate validation reference. Those are required in addition to the numerical gates already passed here.',
  },
};

for (const button of document.querySelectorAll('[data-question]')) {
  button.addEventListener('click', () => {
    const answer = explanationCopy[button.dataset.question];
    if (!answer) return;
    document.querySelectorAll('[data-question]').forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
    document.querySelector('[data-answer-title]').textContent = answer.title;
    document.querySelector('[data-answer-body]').textContent = answer.body;
  });
}

const tabs = [...document.querySelectorAll('[role="tab"]')];
const selectTab = (tab) => {
  tabs.forEach((item) => {
    const selected = item === tab;
    item.setAttribute('aria-selected', String(selected));
    item.tabIndex = selected ? 0 : -1;
    document.getElementById(item.getAttribute('aria-controls')).hidden = !selected;
  });
};
tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => selectTab(tab));
  tab.addEventListener('keydown', (event) => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    let next = index;
    if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
    if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    selectTab(tabs[next]);
    tabs[next].focus();
  });
});

const svgNamespace = 'http://www.w3.org/2000/svg';
const createSvg = (name, attributes = {}) => {
  const element = document.createElementNS(svgNamespace, name);
  Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, value));
  return element;
};
const palette = ['#df7955', '#7b9e92', '#c5a86a', '#7894ab'];

function renderChart(container, series, options = {}) {
  const width = 680;
  const height = 245;
  const plot = { left: 46, right: 16, top: 12, bottom: 31 };
  const all = series.flatMap((item) => item.points).filter((point) => Number.isFinite(point.x) && Number.isFinite(point.y));
  if (!all.length) return;
  const xMin = options.xMin ?? Math.min(...all.map((point) => point.x));
  const xMax = options.xMax ?? Math.max(...all.map((point) => point.x));
  const transformed = all.map((point) => options.log ? Math.log10(Math.max(point.y, 1e-12)) : point.y);
  const yMin = options.yMin ?? Math.min(...transformed);
  const yMax = options.yMax ?? Math.max(...transformed);
  const sx = (value) => plot.left + ((value - xMin) / Math.max(xMax - xMin, 1)) * (width - plot.left - plot.right);
  const sy = (value) => {
    const converted = options.log ? Math.log10(Math.max(value, 1e-12)) : value;
    return plot.top + (1 - (converted - yMin) / Math.max(yMax - yMin, 1e-12)) * (height - plot.top - plot.bottom);
  };
  const svg = createSvg('svg', { viewBox: `0 0 ${width} ${height}`, focusable: 'false' });
  for (let i = 0; i <= 4; i += 1) {
    const y = plot.top + (i / 4) * (height - plot.top - plot.bottom);
    svg.append(createSvg('line', { x1: plot.left, x2: width - plot.right, y1: y, y2: y, stroke: 'currentColor', 'stroke-opacity': '.13' }));
  }
  if (options.threshold !== undefined) {
    const y = sy(options.threshold);
    svg.append(createSvg('line', { x1: plot.left, x2: width - plot.right, y1: y, y2: y, stroke: '#df7955', 'stroke-dasharray': '5 5', 'stroke-width': '1.2' }));
    const label = createSvg('text', { x: width - plot.right, y: Math.max(11, y - 6), fill: '#df7955', 'text-anchor': 'end', 'font-size': '11' });
    label.textContent = `limit ${options.thresholdLabel ?? options.threshold}`;
    svg.append(label);
  }
  series.forEach((item, index) => {
    const path = createSvg('path', {
      d: item.points.map((point, pointIndex) => `${pointIndex ? 'L' : 'M'}${sx(point.x).toFixed(2)} ${sy(point.y).toFixed(2)}`).join(' '),
      fill: 'none', stroke: item.color ?? palette[index % palette.length], 'stroke-width': item.width ?? '1.8', 'vector-effect': 'non-scaling-stroke',
    });
    svg.append(path);
  });
  svg.append(createSvg('line', { x1: plot.left, x2: width - plot.right, y1: height - plot.bottom, y2: height - plot.bottom, stroke: 'currentColor', 'stroke-opacity': '.4' }));
  const xLabel = createSvg('text', { x: width - plot.right, y: height - 8, fill: 'currentColor', 'fill-opacity': '.62', 'text-anchor': 'end', 'font-size': '11' });
  xLabel.textContent = 'outer iteration';
  svg.append(xLabel);
  if (series.length > 1) {
    series.forEach((item, index) => {
      const x = plot.left + index * 77;
      svg.append(createSvg('line', { x1: x, x2: x + 18, y1: height - 9, y2: height - 9, stroke: item.color ?? palette[index], 'stroke-width': '2' }));
      const text = createSvg('text', { x: x + 23, y: height - 5, fill: 'currentColor', 'fill-opacity': '.72', 'font-size': '10' });
      text.textContent = item.label;
      svg.append(text);
    });
  }
  container.replaceChildren(svg);
}

const formatScientific = (value, digits = 3) => Number(value).toExponential(digits);
let telemetry;

try {
  const response = await fetch(`${root}/telemetry.json`, { cache: 'force-cache' });
  if (!response.ok) throw new Error(`Telemetry request returned ${response.status}`);
  telemetry = await response.json();
  renderChart(document.querySelector('[data-chart="residuals"]'), Object.entries(telemetry.residuals).map(([label, points], index) => ({
    label, color: palette[index], points: points.map((point) => ({ x: point.iteration, y: point.initial })),
  })), { log: true, yMin: -6, yMax: 0, threshold: 1e-4, thresholdLabel: '1e−4' });
  renderChart(document.querySelector('[data-chart="mass"]'), [{ points: telemetry.gateSeries.map((point) => ({ x: point.iteration, y: point.massImbalance })) }], { log: true, yMin: -7, yMax: -1.5, threshold: 0.01, thresholdLabel: '1%' });
  renderChart(document.querySelector('[data-chart="energy"]'), [{ points: telemetry.gateSeries.map((point) => ({ x: point.iteration, y: point.energyImbalance })) }], { log: true, yMin: -4.2, yMax: -1.4, threshold: 0.02, thresholdLabel: '2%' });
  renderChart(document.querySelector('[data-chart="mach"]'), [{ points: telemetry.monitors.map((point) => ({ x: point.iteration, y: point.mach })) }], { yMin: 0, yMax: 0.22 });
  document.querySelector('[data-chart-region]').setAttribute('aria-busy', 'false');
} catch (error) {
  document.querySelector('[data-chart-region]').setAttribute('aria-busy', 'false');
  document.querySelectorAll('.chart').forEach((chart) => { chart.textContent = 'Chart data could not be loaded. The numerical text summary remains available.'; });
  console.error('Aero public telemetry load failed.', error);
}

const approve = document.querySelector('[data-approve]');
approve?.addEventListener('click', () => {
  approve.disabled = true;
  approve.textContent = 'Demonstration approved';
  document.querySelector('[data-approval-state]').textContent = 'Approved locally — recorded replay unlocked';
  document.querySelector('[data-replay-stage]').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
});

let replaySpeed = '1';
let animationFrame = null;
const speedButtons = [...document.querySelectorAll('[data-speed]')];
speedButtons.forEach((button) => button.addEventListener('click', () => {
  replaySpeed = button.dataset.speed;
  speedButtons.forEach((item) => item.setAttribute('aria-pressed', String(item === button)));
}));

function monitorAt(iteration) {
  if (!telemetry?.monitors?.length) return null;
  const index = Math.max(0, Math.min(telemetry.monitors.length - 1, Math.floor(iteration)));
  return telemetry.monitors[index];
}

function residualAt(field, iteration) {
  const rows = telemetry?.residuals?.[field];
  if (!rows?.length) return null;
  return rows[Math.max(0, Math.min(rows.length - 1, Math.floor(iteration) - 1))];
}

function updateReplay(iteration) {
  const current = Math.max(0, Math.min(350, Math.floor(iteration)));
  document.querySelector('[data-progress]').value = current;
  document.querySelector('[data-iteration]').textContent = `${current} / 350`;
  for (const field of ['Ux', 'Uy', 'h', 'p']) {
    const row = residualAt(field, current || 1);
    document.querySelector(`[data-value="${field}"]`).textContent = current && row ? formatScientific(row.initial, 2) : '—';
  }
  const monitor = monitorAt(current || 1);
  document.querySelector('[data-value="mach"]').textContent = current && monitor ? monitor.mach.toFixed(7) : '—';
  document.querySelector('[data-value="mass"]').textContent = current && monitor ? `${monitor.mass_flow_outlet.toFixed(9)} kg/s` : '—';
  document.querySelector('[data-value="energy"]').textContent = current && monitor ? formatScientific(monitor.energy_imbalance, 3) : '—';
  document.querySelector('[data-value="gate"]').textContent = current === 350 ? 'Numerical gates pass' : 'Evaluating';
}

document.querySelector('[data-replay-start]')?.addEventListener('click', () => {
  if (!telemetry) {
    document.querySelector('[data-replay-note]').textContent = 'Recorded data is unavailable. The static evidence summaries remain visible.';
    return;
  }
  if (animationFrame) cancelAnimationFrame(animationFrame);
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const instant = replaySpeed === 'instant' || reducedMotion;
  const button = document.querySelector('[data-replay-start]');
  const status = document.querySelector('[data-run-status]');
  button.textContent = 'Replay again';
  status.textContent = instant && reducedMotion ? 'Complete · reduced motion' : 'Replaying recorded evidence';
  if (instant) {
    updateReplay(350);
    status.textContent = 'Completed · numerical gates passed';
    document.querySelector('[data-replay-note]').textContent = 'Recorded solver execution completed. Numerical convergence earned; design readiness remains not established.';
    return;
  }
  const duration = 7180 / Number(replaySpeed);
  const started = performance.now();
  updateReplay(0);
  const frame = (now) => {
    const fraction = Math.min(1, (now - started) / duration);
    updateReplay(fraction * 350);
    if (fraction < 1) animationFrame = requestAnimationFrame(frame);
    else {
      animationFrame = null;
      status.textContent = 'Completed · numerical gates passed';
      document.querySelector('[data-replay-note]').textContent = 'Recorded solver execution completed. Numerical convergence earned; design readiness remains not established.';
    }
  };
  animationFrame = requestAnimationFrame(frame);
});
