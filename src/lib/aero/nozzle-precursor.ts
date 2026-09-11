/** Recorded projection of the authoritative live OpenFOAM result contract.
 *
 * This module does not recompute a verdict. It only maps the retained
 * Aero/cfd/evidence.py output into the workbench display types.
 */
import resultDoc from '../../../public/demos/aero/wall-refinement-v6/engineering-result.json';
import type { EvidenceItem, EvidenceState, NotebookValue, ResultFieldArtifact } from './case';

const ROOT = '/demos/aero/wall-refinement-v6';
type AnyRecord = Record<string, any>;
const result = resultDoc as AnyRecord;

const LABELS: Record<string, string> = {
  run_completed: 'Run completed',
  mesh_quality: 'Mesh quality',
  residual_convergence: 'Residual convergence',
  mass_conservation: 'Mass conservation',
  energy_conservation: 'Energy conservation',
  monitor_stability: 'Monitor stability',
  validation_reference: 'Validation reference',
  model_fidelity: 'Model fidelity',
  mesh_independence: 'Mesh independence',
};

function mapGate(gate: AnyRecord): EvidenceItem {
  return {
    id: String(gate.id),
    label: LABELS[String(gate.id)] ?? String(gate.id),
    status: gate.status,
    required: gate.required === true,
    source: gate.source,
    reason: String(gate.reason ?? ''),
    value: gate.value ?? null,
    limit: gate.limit ?? null,
    units: String(gate.units ?? ''),
    detail: gate.detail ?? {},
  };
}

export const evidence: EvidenceState = {
  execution: {
    status: result.execution.status,
    solverSeconds: result.execution.runtime?.solver_runtime_s ?? null,
    totalSeconds: result.execution.runtime?.request_to_result_s ?? null,
  },
  numerical: {
    status: result.numerical.status,
    gates: (result.numerical.gates ?? []).map(mapGate),
  },
  readiness: {
    status: result.readiness.status,
    gates: (result.readiness.gates ?? []).map(mapGate),
  },
};

function fmt(value: number): string {
  if (value === 0) return '0';
  return Math.abs(value) < 1e-3 ? value.toExponential(3) : String(Number(value.toPrecision(6)));
}

export const monitors: NotebookValue[] = [
  ...Object.entries(result.telemetrySummary?.finalResiduals ?? {}).map(([name, value]) => ({
    label: `${name} final residual`, value: fmt(Number(value)), units: '', source: 'SOLVER_OUTPUT' as const,
  })),
  ...Object.entries(result.telemetrySummary?.monitors ?? {}).filter(([, value]) => typeof value === 'number').map(([name, value]) => ({
    label: name === 'outlet_mass_flow' ? 'Outlet mass flow' : name,
    value: fmt(Number(value)), units: name.includes('mass_flow') ? 'kg/s' : '', source: 'SOLVER_OUTPUT' as const,
  })),
];

export const resultFields: ResultFieldArtifact[] = [{
  field: 'pressure', label: 'Pressure', units: 'Pa',
  href: '/demos/aero/wall-refinement-v6/pressure-surface.json', range: [100004, 101798], source: 'SOLVER_OUTPUT',
}];

export const publicCadArtifact = {
  // The public viewer needs the full solid CAD skin. The solver still uses the
  // hashed axisymmetric wedge in wall-refinement-v6/nozzle.stl; keeping these
  // artifacts separate prevents a thin solver slice from masquerading as a
  // user-facing 3D model while preserving the exact run evidence.
  href: '/demos/aero/shared/nozzle-cutaway.stl', publicFormat: 'stl', type: 'geometry',
  provenance: 'CAD_VISUALIZATION / current parametric nozzle',
  solverInputHref: '/demos/aero/wall-refinement-v6/nozzle.stl',
};

export const publicPressureField = resultFields[0];

export const artifacts = {
  geometry: `${ROOT}/geometry.svg`,
  mesh: null,
  result: null,
};

export const telemetry = result.telemetry;
export const telemetryHref = `${ROOT}/engineering-result.json`;
export const authoritativeResult = result;
export { ROOT as demoRoot };
