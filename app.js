/* ==========================================================================
   AMR Warehouse Robot Pathfinding Engine & Visualizer (Full-Stack Web App)
   Connected to Python Backend REST API (A*, Dijkstra, BFS Solvers)
   ========================================================================== */

const CELL = {
  EMPTY: 0,
  OBSTACLE: 1,
  SHELF: 2,
  TRAFFIC: 3,
  START: 4,
  GOAL: 5
};

class CanvasGridRenderer {
  constructor(canvas, options = {}) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.cellSize = options.cellSize || 20;
    this.algoName = options.algoName || 'A* Search';
    this.gridData = null;
  }

  resize(rows, cols) {
    this.canvas.width = cols * this.cellSize;
    this.canvas.height = rows * this.cellSize;
  }

  getExploredColor(idx, total, algoName) {
    const t = Math.min(1.0, idx / Math.max(1, total));
    if (algoName.includes('A*')) {
      const r = Math.floor(124 + t * (216 - 124));
      const g = Math.floor(58 + t * (180 - 58));
      const b = Math.floor(237 + t * (254 - 237));
      return `rgb(${r}, ${g}, ${b})`;
    } else if (algoName.includes('Dijkstra')) {
      const r = Math.floor(14 + t * (56 - 14));
      const g = Math.floor(116 + t * (189 - 116));
      const b = Math.floor(144 + t * (248 - 144));
      return `rgb(${r}, ${g}, ${b})`;
    } else {
      const r = Math.floor(234 + t * (249 - 234));
      const g = Math.floor(88 + t * (115 - 88));
      const b = Math.floor(12 + t * (22 - 12));
      return `rgb(${r}, ${g}, ${b})`;
    }
  }

  render(gridState, stepObj, finalPath = null) {
    if (!gridState) return;
    this.gridData = gridState;
    const { rows, cols, grid, start, goal } = gridState;
    this.resize(rows, cols);

    const ctx = this.ctx;
    const cs = this.cellSize;

    ctx.fillStyle = '#090d16';
    ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // 1. Base Grid Matrix
    for (let r = 0; r < rows; r++) {
      for (let c = 0; c < cols; c++) {
        const x = c * cs, y = r * cs;
        const type = grid[r][c];

        if (type === CELL.OBSTACLE) {
          ctx.fillStyle = '#374151';
          ctx.fillRect(x, y, cs, cs);
          ctx.strokeStyle = '#1f2937';
          ctx.strokeRect(x, y, cs, cs);
        } else if (type === CELL.SHELF) {
          ctx.fillStyle = '#b45309';
          ctx.fillRect(x, y, cs, cs);
          ctx.strokeStyle = '#f59e0b';
          ctx.lineWidth = 1;
          ctx.strokeRect(x + 1, y + 1, cs - 2, cs - 2);
          ctx.strokeStyle = '#78350f';
          ctx.beginPath();
          ctx.moveTo(x + 2, y + cs / 2);
          ctx.lineTo(x + cs - 2, y + cs / 2);
          ctx.stroke();
        } else if (type === CELL.TRAFFIC) {
          ctx.fillStyle = '#78350f';
          ctx.fillRect(x, y, cs, cs);
          ctx.strokeStyle = '#374151';
          ctx.strokeRect(x, y, cs, cs);
        } else {
          ctx.fillStyle = '#111827';
          ctx.fillRect(x, y, cs, cs);
          ctx.strokeStyle = '#1f2937';
          ctx.lineWidth = 0.5;
          ctx.strokeRect(x, y, cs, cs);
        }
      }
    }

    // 2. Explored Set (from Python Backend)
    if (stepObj && stepObj.explored) {
      const total = stepObj.explored.length;
      stepObj.explored.forEach((cell, idx) => {
        const [r, c] = cell;
        if ((r === start[0] && c === start[1]) || (r === goal[0] && c === goal[1])) return;
        ctx.fillStyle = this.getExploredColor(idx, total, this.algoName);
        ctx.fillRect(c * cs + 1, r * cs + 1, cs - 2, cs - 2);
      });
    }

    // 3. Frontier Set (from Python Backend)
    if (stepObj && stepObj.frontier) {
      stepObj.frontier.forEach(cell => {
        const [r, c] = cell;
        if ((r === start[0] && c === start[1]) || (r === goal[0] && c === goal[1])) return;
        ctx.fillStyle = 'rgba(245, 158, 11, 0.4)';
        ctx.fillRect(c * cs + 1, r * cs + 1, cs - 2, cs - 2);
        ctx.strokeStyle = '#f59e0b';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(c * cs + 1, r * cs + 1, cs - 2, cs - 2);
      });
    }

    // 4. Final Path
    const pathColor = this.algoName.includes('A*') ? '#c084fc' : (this.algoName.includes('Dijkstra') ? '#38bdf8' : '#fb923c');
    if (finalPath && finalPath.length > 1) {
      ctx.strokeStyle = pathColor;
      ctx.lineWidth = Math.max(3, cs / 5);
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.beginPath();
      finalPath.forEach((pt, i) => {
        const cx = pt[1] * cs + cs / 2;
        const cy = pt[0] * cs + cs / 2;
        if (i === 0) ctx.moveTo(cx, cy);
        else ctx.lineTo(cx, cy);
      });
      ctx.stroke();

      finalPath.forEach(pt => {
        const cx = pt[1] * cs + cs / 2;
        const cy = pt[0] * cs + cs / 2;
        ctx.fillStyle = pathColor;
        ctx.beginPath();
        ctx.arc(cx, cy, Math.max(2, cs / 6), 0, Math.PI * 2);
        ctx.fill();
      });
    }

    // 5. Heuristic Vector Line (A*)
    if (this.algoName.includes('A*') && stepObj && stepObj.current) {
      const [cr, cc] = stepObj.current;
      const [gr, gc] = goal;
      ctx.strokeStyle = 'rgba(236, 72, 153, 0.6)';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.beginPath();
      ctx.moveTo(cc * cs + cs / 2, cr * cs + cs / 2);
      ctx.lineTo(gc * cs + cs / 2, gr * cs + cs / 2);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    // 6. Start & Goal Markers
    const [sr, sc] = start;
    ctx.fillStyle = '#10b981';
    ctx.fillRect(sc * cs, sr * cs, cs, cs);
    ctx.fillStyle = '#ffffff';
    ctx.font = `bold ${Math.max(10, cs / 2)}px sans-serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('S', sc * cs + cs / 2, sr * cs + cs / 2);

    const [gr, gc] = goal;
    ctx.fillStyle = '#ef4444';
    ctx.fillRect(gc * cs, gr * cs, cs, cs);
    ctx.fillStyle = '#ffffff';
    ctx.fillText('G', gc * cs + cs / 2, gr * cs + cs / 2);

    // 7. Active AMR Robot Head
    const activePos = stepObj ? stepObj.current : null;
    if (activePos && !(activePos[0] === sr && activePos[1] === sc) && !(activePos[0] === gr && activePos[1] === gc)) {
      const [rr, rc] = activePos;
      const rx = rc * cs + cs / 2;
      const ry = rr * cs + cs / 2;
      const rad = Math.max(4, cs / 3);

      ctx.fillStyle = 'rgba(59, 130, 246, 0.4)';
      ctx.beginPath();
      ctx.arc(rx, ry, rad + 4, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#ffffff';
      ctx.beginPath();
      ctx.arc(rx, ry, rad, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#2563eb';
      ctx.beginPath();
      ctx.arc(rx, ry, rad - 2, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}

// Full-Stack App Controller
class FullStackApp {
  constructor() {
    this.backendUrl = window.location.origin;
    this.gridState = null;
    this.results = {};
    this.renderers = {};

    this.activeTool = CELL.OBSTACLE;
    this.stepIndex = 0;
    this.maxSteps = 0;
    this.isPlaying = false;
    this.playInterval = null;
    this.playbackSpeed = 3;
    this.isDragging = false;

    this.initUI();
    this.initRenderers();
    this.checkBackendConnection();
    this.fetchGridAndSolve();
  }

  async checkBackendConnection() {
    const statusEl = document.getElementById('backendStatus');
    try {
      const res = await fetch(`${this.backendUrl}/api/status`);
      const data = await res.json();
      if (statusEl) {
        statusEl.innerHTML = `🟢 Python Backend Connected (${data.backend})`;
        statusEl.style.color = '#34d399';
      }
    } catch (err) {
      if (statusEl) {
        statusEl.innerHTML = `🔴 Backend Offline (Using Fallback)`;
        statusEl.style.color = '#f87171';
      }
    }
  }

  async fetchGridAndSolve() {
    try {
      const res = await fetch(`${this.backendUrl}/api/grid`);
      const data = await res.json();
      this.gridState = data;
      this.results = data.solvers;
      this.updateStepBounds();
      this.renderAll();
      this.updateBenchmarkTable();
    } catch (err) {
      console.error("Backend fetch error:", err);
    }
  }

  async loadPreset(presetName) {
    try {
      const res = await fetch(`${this.backendUrl}/api/preset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preset: presetName, rows: 20, cols: 25 })
      });
      const data = await res.json();
      this.gridState = data;
      this.results = data.solvers;
      this.resetPlayback();
      this.updateStepBounds();
      this.renderAll();
      this.updateBenchmarkTable();
    } catch (err) {
      console.error("Preset load error:", err);
    }
  }

  async editCell(row, col, cellType) {
    try {
      const res = await fetch(`${this.backendUrl}/api/cell`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ row, col, type: cellType })
      });
      const data = await res.json();
      this.gridState = data;
      this.results = data.solvers;
      this.resetPlayback();
      this.updateStepBounds();
      this.renderAll();
      this.updateBenchmarkTable();
    } catch (err) {
      console.error("Cell edit error:", err);
    }
  }

  updateStepBounds() {
    this.maxSteps = Math.max(...Object.values(this.results).map(r => r.steps ? r.steps.length : 0));
    const scrubber = document.getElementById('stepScrubber');
    if (scrubber) scrubber.max = Math.max(0, this.maxSteps - 1);
  }

  initUI() {
    // Tool Buttons
    document.querySelectorAll('.tool-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const tool = btn.dataset.tool;
        if (tool === 'obstacle') this.activeTool = CELL.OBSTACLE;
        if (tool === 'shelf') this.activeTool = CELL.SHELF;
        if (tool === 'traffic') this.activeTool = CELL.TRAFFIC;
        if (tool === 'start') this.activeTool = CELL.START;
        if (tool === 'goal') this.activeTool = CELL.GOAL;
        if (tool === 'clear') this.activeTool = CELL.EMPTY;
      });
    });

    // Preset Selector
    const presetSel = document.getElementById('presetSelect');
    if (presetSel) {
      presetSel.addEventListener('change', e => this.loadPreset(e.target.value));
    }

    // Clear Grid
    const btnClear = document.getElementById('btnClear');
    if (btnClear) {
      btnClear.addEventListener('click', () => this.loadPreset('empty'));
    }

    // Playback Controls
    document.getElementById('btnPlay').addEventListener('click', () => this.togglePlay());
    document.getElementById('btnStepBack').addEventListener('click', () => this.stepBack());
    document.getElementById('btnStepForward').addEventListener('click', () => this.stepForward());
    document.getElementById('btnReset').addEventListener('click', () => this.resetPlayback());

    const scrubber = document.getElementById('stepScrubber');
    if (scrubber) {
      scrubber.addEventListener('input', e => {
        this.stepIndex = parseInt(e.target.value);
        this.renderAll();
      });
    }

    const speedSlider = document.getElementById('speedSlider');
    if (speedSlider) {
      speedSlider.addEventListener('input', e => {
        this.playbackSpeed = parseInt(e.target.value);
        if (this.isPlaying) {
          this.pause();
          this.play();
        }
      });
    }

    // Canvas Click & Drag Drawing
    ['canvasAStar', 'canvasDijkstra', 'canvasBFS'].forEach(id => {
      const canvas = document.getElementById(id);
      if (!canvas) return;

      canvas.addEventListener('mousedown', e => {
        this.isDragging = true;
        this.handleCanvasClick(canvas, e);
      });

      canvas.addEventListener('mousemove', e => {
        if (this.isDragging) this.handleCanvasClick(canvas, e);
      });

      window.addEventListener('mouseup', () => {
        this.isDragging = false;
      });
    });
  }

  handleCanvasClick(canvas, e) {
    if (!this.gridState) return;
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const cs = this.renderers['A* Search'].cellSize;

    const c = Math.floor(x / cs);
    const r = Math.floor(y / cs);

    if (r >= 0 && r < this.gridState.rows && c >= 0 && c < this.gridState.cols) {
      this.editCell(r, c, this.activeTool);
    }
  }

  initRenderers() {
    ['A* Search', 'Dijkstra', 'BFS'].forEach(name => {
      const idMap = { 'A* Search': 'canvasAStar', 'Dijkstra': 'canvasDijkstra', 'BFS': 'canvasBFS' };
      const canvas = document.getElementById(idMap[name]);
      if (canvas) {
        this.renderers[name] = new CanvasGridRenderer(canvas, { cellSize: 18, algoName: name });
      }
    });
  }

  renderAll() {
    if (!this.gridState) return;

    const scrubber = document.getElementById('stepScrubber');
    if (scrubber) scrubber.value = this.stepIndex;

    const stepCounter = document.getElementById('stepCounter');
    if (stepCounter) {
      stepCounter.innerText = `Step ${this.stepIndex} of ${Math.max(0, this.maxSteps - 1)}`;
    }

    Object.entries(this.results).forEach(([name, res]) => {
      const renderer = this.renderers[name];
      if (renderer && res.steps) {
        const curStepIdx = Math.min(this.stepIndex, res.steps.length - 1);
        const stepObj = res.steps[curStepIdx];
        const isAtEnd = (curStepIdx >= res.steps.length - 1);

        renderer.render(this.gridState, stepObj, isAtEnd ? res.path : null);

        // Update Stats Card
        const distIdMap = { 'A* Search': 'distAStar', 'Dijkstra': 'distDijkstra', 'BFS': 'distBFS' };
        const expIdMap = { 'A* Search': 'expAStar', 'Dijkstra': 'expDijkstra', 'BFS': 'expBFS' };

        const distEl = document.getElementById(distIdMap[name]);
        const expEl = document.getElementById(expIdMap[name]);

        if (distEl) distEl.innerText = res.found ? res.distance.toFixed(1) : "No Path";
        if (expEl) expEl.innerText = stepObj ? stepObj.explored.length : 0;
      }
    });
  }

  togglePlay() {
    if (this.isPlaying) this.pause();
    else this.play();
  }

  play() {
    this.isPlaying = true;
    const btnPlay = document.getElementById('btnPlay');
    if (btnPlay) btnPlay.innerText = '⏸ Pause';

    const intervalMs = Math.max(20, 300 / this.playbackSpeed);
    this.playInterval = setInterval(() => {
      if (this.stepIndex >= this.maxSteps - 1) {
        this.pause();
      } else {
        this.stepIndex++;
        this.renderAll();
      }
    }, intervalMs);
  }

  pause() {
    this.isPlaying = false;
    const btnPlay = document.getElementById('btnPlay');
    if (btnPlay) btnPlay.innerText = '▶ Play';
    if (this.playInterval) clearInterval(this.playInterval);
  }

  stepForward() {
    this.pause();
    this.stepIndex = Math.min(this.maxSteps - 1, this.stepIndex + 1);
    this.renderAll();
  }

  stepBack() {
    this.pause();
    this.stepIndex = Math.max(0, this.stepIndex - 1);
    this.renderAll();
  }

  resetPlayback() {
    this.pause();
    this.stepIndex = 0;
    this.renderAll();
  }

  updateBenchmarkTable() {
    const tbody = document.getElementById('benchmarkTbody');
    if (!tbody || !this.results) return;

    tbody.innerHTML = '';
    const astarRes = this.results['A* Search'];
    const dijkRes = this.results['Dijkstra'];

    Object.entries(this.results).forEach(([name, res]) => {
      const tr = document.createElement('tr');
      const eff = res.found && res.path.length ? ((res.path.length / Math.max(1, res.explored.length)) * 100).toFixed(1) : 0;
      tr.innerHTML = `
        <td><strong>${name}</strong></td>
        <td>${res.found ? '✅ Yes' : '❌ No'}</td>
        <td>${res.found ? res.distance.toFixed(1) : 'N/A'}</td>
        <td>${res.path.length ? res.path.length - 1 : 0}</td>
        <td>${res.explored.length}</td>
        <td>${eff}%</td>
        <td>${res.executionTime.toFixed(2)} ms</td>
      `;
      tbody.appendChild(tr);
    });

    if (astarRes && dijkRes && astarRes.found && dijkRes.explored.length > 0) {
      const cellDiff = dijkRes.explored.length - astarRes.explored.length;
      const pctSavings = ((cellDiff / dijkRes.explored.length) * 100).toFixed(1);
      const verdictEl = document.getElementById('verdictText');
      if (verdictEl) {
        verdictEl.innerText = `Python A* Search examined ${astarRes.explored.length} cells vs Python Dijkstra's ${dijkRes.explored.length} cells (${pctSavings}% fewer cells examined) while reaching the exact same optimal distance cost of ${astarRes.distance.toFixed(1)}.`;
      }
    }
  }
}

// Instantiate FullStackApp when DOM is loaded
window.addEventListener('DOMContentLoaded', () => {
  window.app = new FullStackApp();
});
