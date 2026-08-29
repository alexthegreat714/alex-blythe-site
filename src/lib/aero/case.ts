/**
 * Shared state model for the Aero Engineering Workbench.
 *
 * One EngineeringCase is the single source of truth for four surfaces:
 * Notebook, Viewport, Chat and Evidence. Nothing in the UI is permitted to
 * assert an engineering verdict that does not originate here.
 *
 * Deliberately small. This is a shared contract, not a framework.
 */

/* -------------------------------------------------------------------------
 * provenance
 * ---------------------------------------------------------------------- */

/** Where a displayed value came from. Aero interpretation is never presented
 *  as if it were solver measurement. */
export type Provenance =
  | 'USER_INPUT'
  | 'CASE_CONFIGURATION'
  | 'ANALYTICAL'
  | 'SOLVER_OUTPUT'
  | 'DERIVED'
  | 'VALIDATION_REFERENCE'
  | 'AERO_INTERPRETATION';

export const PROVENANCE_LABEL: Record<Provenance, string> = {
  USER_INPUT: 'User input',
  CASE_CONFIGURATION: 'Case configuration',
  ANALYTICAL: 'Analytical',
  SOLVER_OUTPUT: 'Solver output',
  DERIVED: 'Derived result',
  VALIDATION_REFERENCE: 'Validation reference',
  AERO_INTERPRETATION: 'Aero interpretation',
};

/* -------------------------------------------------------------------------
 * evidence
 * ---------------------------------------------------------------------- */

/** Four states. NOT_EVALUATED is never PASS. Mirrors Aero/cfd/evidence.py. */
export type GateStatus = 'PASS' | 'FAIL' | 'NOT_EVALUATED' | 'NOT_APPLICABLE' | 'MISSING';

export type AggregateStatus = 'PASS' | 'FAIL' | 'NOT_ESTABLISHED';
export type ReadinessStatus = 'READY' | 'NOT_READY' | 'NOT_ESTABLISHED';

export interface EvidenceItem {
  id: string;
  label: string;
  status: GateStatus;
  required: boolean;
  source: Provenance;
  reason: string;
  value?: number | null;
  limit?: number | null;
  units?: string;
  detail?: Record<string, unknown>;
}

export interface EvidenceState {
  execution: {
    status: RunStatus;
    /** Null when the run predates runtime instrumentation. Render NOT RECORDED. */
    solverSeconds: number | null;
    totalSeconds: number | null;
  };
  numerical: { status: AggregateStatus; gates: EvidenceItem[] };
  readiness: { status: ReadinessStatus; gates: EvidenceItem[] };
}

/* -------------------------------------------------------------------------
 * run lifecycle
 * ---------------------------------------------------------------------- */

/** COMPLETE means the authoritative execution+evidence lifecycle finished.
 *  It is never inferred from a solver process exiting. */
export type RunStatus =
  | 'IDLE'
  | 'PROPOSED'
  | 'AWAITING_APPROVAL'
  | 'QUEUED'
  | 'PREFLIGHT'
  | 'GEOMETRY_CASE_PREPARATION'
  | 'MESH'
  | 'SOLVER_START'
  | 'SOLVING'
  | 'POST_PROCESSING'
  | 'EVIDENCE_EVALUATION'
  | 'COMPLETE'
  | 'FAILED'
  | 'TIMED_OUT'
  | 'CANCELLED';

export type RunMode = 'RECORDED' | 'LIVE';

export interface RunState {
  runId: string;
  status: RunStatus;
  /** RECORDED execution is never presented as LIVE. */
  mode: RunMode;
  meshLevel?: string;
  proposal?: RunProposal | null;
}

export interface RunProposal {
  caseLabel: string;
  parameter: string;
  value: number;
  units: string;
  solver: string;
  /** Immutable once approved. */
  frozen: boolean;
}

/* -------------------------------------------------------------------------
 * viewport
 * ---------------------------------------------------------------------- */

export type ViewportMode = 'geometry' | 'mesh' | 'result';
export type ResultField = 'pressure' | 'velocity' | 'mach' | 'temperature';

export interface ViewportState {
  mode: ViewportMode;
  /** Null until a result field is both available and selected. */
  field: ResultField | null;
  meshVisible: boolean;
  selectedProbe: { x: number; y: number; label?: string } | null;
  camera: { zoom: number; panX: number; panY: number };
  legendRange: [number, number] | null;
  runId: string;
}

export const DEFAULT_VIEWPORT: ViewportState = {
  mode: 'geometry',
  field: null,
  meshVisible: false,
  selectedProbe: null,
  camera: { zoom: 1, panX: 0, panY: 0 },
  legendRange: null,
  runId: '',
};

/* -------------------------------------------------------------------------
 * notebook
 * ---------------------------------------------------------------------- */

export type NotebookSectionId =
  | 'problem'
  | 'requirements-knowns'
  | 'assumptions'
  | 'physics'
  | 'first-order'
  | 'geometry'
  | 'boundary-conditions'
  | 'model-fidelity'
  | 'numerical-method'
  | 'acceptance'
  | 'execution'
  | 'evidence'
  | 'interpretation';

export interface SymbolDefinition {
  symbol: string;
  meaning: string;
  units?: string;
}

export interface EquationBlock {
  title: string;
  latex: string;
  symbols: SymbolDefinition[];
  /** Why this equation matters for THIS case, not a textbook gloss. */
  meaning: string;
  source: Provenance;
}

export interface NotebookValue {
  label: string;
  value: string;
  units?: string;
  source: Provenance;
}

export interface NotebookSection {
  id: NotebookSectionId;
  index: string;
  title: string;
  body?: string[];
  values?: NotebookValue[];
  equations?: EquationBlock[];
  /** Rendered when the section has a framework but no established content. */
  notEstablished?: string;
}

/* -------------------------------------------------------------------------
 * first-order analysis
 * ---------------------------------------------------------------------- */

/** INPUTS -> EQUATION -> ESTIMATE -> EXPECTED TREND -> NUMERICAL COMPARISON.
 *  `estimate` and `comparison` stay null until an authoritative hand
 *  calculation exists; the component renders NOT YET ESTABLISHED rather than
 *  inventing one. */
export interface FirstOrderAnalysis {
  title: string;
  inputs: NotebookValue[];
  equation: EquationBlock | null;
  estimate: { label: string; value: string; units?: string } | null;
  expectedTrend: string | null;
  numericalResult: { label: string; value: string; units?: string } | null;
  comparison: { label: string; value: string; established: boolean } | null;
}

export type GeometryProvenance =
  | 'USER_PROVIDED'
  | 'PARAMETRIC_GENERATED'
  | 'IMPORTED'
  | 'CAD_GENERATED';

export interface GeometryDefinition {
  status: 'READY' | 'GEOMETRY_REQUIRED' | 'PROPOSED';
  provenance: GeometryProvenance | null;
  generator: string | null;
  description: string;
  parameters: Record<string, number>;
  generationRequiresApproval: boolean;
}

export interface AcceptanceCriterion {
  id: string;
  required: boolean;
  criterion?: string;
  [key: string]: unknown;
}

export interface TelemetryPoint {
  sample: number;
  value?: number;
  imbalance?: number;
  throughput?: number;
  fraction?: number | null;
}

export interface WorkbenchTelemetry {
  residuals: Record<string, TelemetryPoint[]>;
  massConservation: TelemetryPoint[];
  energyConservation: TelemetryPoint[];
  monitors: Record<string, TelemetryPoint[]>;
  basis?: Record<string, string>;
}

/* -------------------------------------------------------------------------
 * chat + action contract
 * ---------------------------------------------------------------------- */

/** Strict allowlist. Arbitrary JavaScript and arbitrary tool names are never
 *  executed from model output; anything not on this list is discarded. */
export const WORKBENCH_ACTIONS = [
  'SHOW_NOTEBOOK_SECTION',
  'SHOW_ANALYSIS_STEP',
  'SET_VIEWPORT_MODE',
  'SET_RESULT_FIELD',
  'TOGGLE_MESH',
  'RESET_CAMERA',
  'SELECT_RUN',
  'COMPARE_RUNS',
  'EXPLAIN_GATE',
  'PROPOSE_PARAMETER_CHANGE',
  'PROPOSE_GEOMETRY',
  'REQUEST_RUN',
  'REQUEST_MESH_STUDY',
  'REQUEST_WALL_RESOLVED_MESH_STUDY',
] as const;

export type WorkbenchActionName = (typeof WORKBENCH_ACTIONS)[number];

export interface WorkbenchAction {
  action: WorkbenchActionName;
  section?: NotebookSectionId;
  analysisStep?: 'scope' | 'area' | 'density' | 'velocity' | 'mach' | 'dynamic-pressure' | 'limits';
  mode?: ViewportMode;
  field?: ResultField;
  visible?: boolean;
  runId?: string;
  gateId?: string;
  parameter?: string;
  value?: number;
  geometryType?: 'AXISYMMETRIC_NOZZLE_V1' | 'AXISYMMETRIC_NOZZLE_WEDGE_V1';
  parameters?: Record<string, number>;
  meshSizesM?: number[];
  meshLevels?: number[];
}

function finiteNumberRecord(raw: unknown): Record<string, number> | null {
  if (!raw || typeof raw !== 'object' || Array.isArray(raw)) return null;
  const entries = Object.entries(raw as Record<string, unknown>);
  if (!entries.length || entries.some(([, value]) => typeof value !== 'number' || !Number.isFinite(value))) {
    return null;
  }
  return Object.fromEntries(entries) as Record<string, number>;
}

/** Validate an untrusted action object against the allowlist.
 *  Returns null for anything unrecognised, malformed, or out of range. */
export function validateAction(raw: unknown): WorkbenchAction | null {
  if (!raw || typeof raw !== 'object') return null;
  const candidate = raw as Record<string, unknown>;
  const name = candidate.action;
  if (typeof name !== 'string') return null;
  if (!(WORKBENCH_ACTIONS as readonly string[]).includes(name)) return null;

  const out: WorkbenchAction = { action: name as WorkbenchActionName };

  switch (name) {
    case 'SHOW_NOTEBOOK_SECTION': {
      const s = candidate.section;
      if (typeof s !== 'string') return null;
      out.section = s as NotebookSectionId;
      return out;
    }
    case 'SHOW_ANALYSIS_STEP': {
      const step = candidate.analysisStep;
      if (!['scope', 'area', 'density', 'velocity', 'mach', 'dynamic-pressure', 'limits'].includes(String(step))) return null;
      out.analysisStep = step as WorkbenchAction['analysisStep'];
      return out;
    }
    case 'SET_VIEWPORT_MODE': {
      const m = candidate.mode;
      if (m !== 'geometry' && m !== 'mesh' && m !== 'result') return null;
      out.mode = m;
      return out;
    }
    case 'SET_RESULT_FIELD': {
      const f = candidate.field;
      if (f !== 'pressure' && f !== 'velocity' && f !== 'mach' && f !== 'temperature') return null;
      out.field = f;
      return out;
    }
    case 'TOGGLE_MESH': {
      out.visible = typeof candidate.visible === 'boolean' ? candidate.visible : undefined;
      return out;
    }
    case 'RESET_CAMERA':
      return out;
    case 'SELECT_RUN':
    case 'COMPARE_RUNS': {
      if (typeof candidate.runId !== 'string') return null;
      out.runId = candidate.runId;
      return out;
    }
    case 'EXPLAIN_GATE': {
      if (typeof candidate.gateId !== 'string') return null;
      out.gateId = candidate.gateId;
      return out;
    }
    case 'PROPOSE_PARAMETER_CHANGE':
    case 'REQUEST_RUN': {
      if (typeof candidate.parameter !== 'string') return null;
      if (typeof candidate.value !== 'number' || !Number.isFinite(candidate.value)) return null;
      out.parameter = candidate.parameter;
      out.value = candidate.value;
      return out;
    }
    case 'PROPOSE_GEOMETRY': {
      if (candidate.geometryType !== 'AXISYMMETRIC_NOZZLE_V1') return null;
      const parameters = finiteNumberRecord(candidate.parameters);
      if (!parameters) return null;
      out.geometryType = candidate.geometryType;
      out.parameters = parameters;
      return out;
    }
    case 'REQUEST_MESH_STUDY': {
      if (candidate.geometryType !== 'AXISYMMETRIC_NOZZLE_V1') return null;
      const parameters = finiteNumberRecord(candidate.parameters);
      if (!parameters) return null;
      const levels = candidate.meshSizesM;
      if (!Array.isArray(levels) || levels.length !== 3 || levels.some((value, index) => value !== [0.005, 0.004, 0.003][index])) return null;
      out.geometryType = candidate.geometryType;
      out.parameters = parameters;
      out.meshSizesM = [...levels] as number[];
      return out;
    }
    case 'REQUEST_WALL_RESOLVED_MESH_STUDY': {
      if (candidate.geometryType !== 'AXISYMMETRIC_NOZZLE_WEDGE_V1') return null;
      const parameters = finiteNumberRecord(candidate.parameters);
      if (!parameters) return null;
      const levels = candidate.meshLevels;
      if (!Array.isArray(levels) || levels.length !== 3 || levels.some((value, index) => value !== [2, 3, 4][index])) return null;
      out.geometryType = candidate.geometryType;
      out.parameters = parameters;
      out.meshLevels = [...levels] as number[];
      return out;
    }
    default:
      return null;
  }
}

export interface ChatTurn {
  role: 'aero' | 'user';
  text: string;
  /** Actions the turn requests. Validated before any is applied. */
  actions?: WorkbenchAction[];
  source: Provenance;
}

/* -------------------------------------------------------------------------
 * the case
 * ---------------------------------------------------------------------- */

export interface ResultFieldArtifact {
  field: ResultField;
  label: string;
  units: string;
  /** Public-safe artifact path. Local filesystem paths never reach the client. */
  href: string;
  range: [number, number] | null;
  source: Provenance;
}

export interface EngineeringCase {
  schema?: 'aero.engineering.case.v2';
  id: string;
  discipline: 'CFD' | 'FEA' | 'THERMAL' | 'STRUCTURAL_DYNAMICS' | 'OPTIMIZATION';
  title: string;
  solver: string;
  mode: RunMode;
  sections: NotebookSection[];
  firstOrder: FirstOrderAnalysis;
  artifacts: {
    geometry: string | null;
    mesh: string | null;
    result: string | null;
  };
  resultFields: ResultFieldArtifact[];
  evidence: EvidenceState;
  run: RunState;
  monitors: NotebookValue[];
  problemStatement?: string;
  requirements?: string[];
  knownValues?: Array<{ label: string; value: unknown; units: string; source: Provenance }>;
  unknowns?: string[];
  assumptions?: string[];
  equations?: Array<EquationBlock & { id: string; mathml: string; expression: string }>;
  analyticalCalculations?: Array<Record<string, unknown>>;
  expectedPhysicalTrends?: string[];
  geometry?: GeometryDefinition;
  geometryContract?: Record<string, unknown>;
  mesh?: Record<string, unknown>;
  boundaryConditions?: Array<Record<string, unknown>>;
  fidelityModel?: Record<string, unknown>;
  numericalMethod?: Record<string, unknown>;
  predeclaredAcceptanceCriteria?: AcceptanceCriterion[];
  validationRequirements?: string[];
  telemetry?: WorkbenchTelemetry;
  aeroInterpretation?: string;
}

/** Human labels for statuses; also used for the non-colour cue required by
 *  the accessibility rules (status text always accompanies the swatch). */
export const STATUS_LABEL: Record<GateStatus | AggregateStatus | ReadinessStatus, string> = {
  PASS: 'PASS',
  FAIL: 'FAIL',
  NOT_EVALUATED: 'NOT EVALUATED',
  NOT_APPLICABLE: 'NOT APPLICABLE',
  MISSING: 'MISSING',
  NOT_ESTABLISHED: 'NOT ESTABLISHED',
  READY: 'READY',
  NOT_READY: 'NOT READY',
};
