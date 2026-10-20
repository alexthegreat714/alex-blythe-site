// Public allowlist only. No private observer inputs or machine identifiers.
export const phaseSpecs = [
  ['heldout_base_r0',48],['heldout_candidate002_r0',48],
  ['heldout_base_r1',48],['heldout_candidate002_r1',48],
  ['named_base_r0',240],['named_candidate002_r0',240],
  ['historical_base_r0',48],['historical_candidate002_r0',48],
  ['historical_base_r1',48],['historical_candidate002_r1',48],
] as const;
export const closureLabels = {controller_exited:'Controller exit',owned_workers_cleared:'Owned workers and GPU contexts cleared',logs_closed:'Log closure',reservation_released:'Exact reservation release',custody_verified:'Artifact custody rechecked'};
const active = ['RUNNING','INITIALIZING','CHECKING','FINALIZING'];
export function valid(s:any) {
  if (!s || s.schema !== 'aero.public.candidate002.validation.v2' || s.total_outputs !== 864 || ![...active,'UNKNOWN','INCOMPLETE_STOPPED','COLLECTED_REVIEW_PENDING'].includes(s.state)) return false;
  if (s.run_label !== 'Validation attempt 4 · 20 October 2026' || s.publication_mode !== 'IDENTITY_VERIFIED_PERIODIC_SNAPSHOT' || s.stale_after_seconds !== 1200 || s.refresh_interval_seconds !== 900) return false;
  if (!Array.isArray(s.phases) || s.phases.length !== 10 || !s.closure || Object.keys(closureLabels).some(k => typeof s.closure[k] !== 'boolean')) return false;
  if (s.training_steps !== null && s.training_steps !== 858) return false;
  if (s.evaluation_status !== 'NOT_ESTABLISHED' || s.promotion_status !== 'NOT_AUTHORIZED') return false;
  if (!Number.isFinite(Date.parse(s.published_at))) return false;
  if (s.phases.some((p:any,i:number) => !p || p.id !== phaseSpecs[i][0] || p.total !== phaseSpecs[i][1] || !['unknown','not_started','initializing','running','stopped','outputs_saved'].includes(p.state) || (p.saved !== null && (!Number.isInteger(p.saved) || p.saved < 0 || p.saved > p.total)) || (p.state === 'not_started' && p.saved !== 0) || (p.state === 'outputs_saved' && p.saved !== p.total))) return false;
  if (s.last_phase !== null && !phaseSpecs.some(p=>p[0] === s.last_phase)) return false;
  if (active.includes(s.state) && Object.values(s.closure).some(Boolean)) return false;
  if (s.state === 'UNKNOWN') return s.saved_outputs === null && s.percent === null && !s.collection_complete && s.phases.every((p:any) => p.saved === null) && Object.values(s.closure).every(v=>v === false);
  if (!Number.isFinite(Date.parse(s.observed_at)) || !Number.isInteger(s.gate_breach_count) || s.gate_breach_count < 0) return false;
  const known = s.phases.every((p:any)=>Number.isInteger(p.saved));
  const sum = known ? s.phases.reduce((n:number,p:any)=>n+p.saved,0) : null;
  return s.saved_outputs === sum && s.percent === (sum === null ? null : Math.round(sum / 864 * 1000) / 10) && s.collection_complete === (s.state === 'COLLECTED_REVIEW_PENDING') && (!s.collection_complete || sum === 864);
}
export function view(s:any, now:number, failed=false) {
  const periodic = active.includes(s.state);
  const age = (now - Date.parse(s.observed_at))/1000;
  const stale = periodic && (!Number.isFinite(age) || age > 1200 || age < -5);
  let pill = ({RUNNING:'Last observed running', INITIALIZING:'Model initializing', CHECKING:'Between phases / checking', FINALIZING:'Finalization pending', INCOMPLETE_STOPPED:'Stopped · incomplete', COLLECTED_REVIEW_PENDING:'Collected · review pending', UNKNOWN:'Status unknown'} as any)[s.state];
  let activity = ({RUNNING:'Identity-verified validation worker is active at the observation time. Saved responses are collection progress, not a quality score or proof against stalling.', INITIALIZING:'Identity-verified worker is initializing a model. Missing output counts remain unknown; model loading is not validation completion.', CHECKING:'Supervisor and authority heartbeat verified; no active worker was established in this snapshot. This is not proof of useful learning.', FINALIZING:'Execution reported a terminal outcome; process exit and final restoration are still being checked.', INCOMPLETE_STOPPED:'Validation stopped incomplete. Saved evidence is retained; no automatic restart is authorized.', COLLECTED_REVIEW_PENDING:'Response collection finished. Scoring and review are separate.', UNKNOWN:'Execution status is unknown. Missing or unverified data is not zero progress.'} as any)[s.state];
  if (stale) {pill='Observation stale';activity='The execution observation is over 20 minutes old or its clock is inconsistent. Showing last observed counts; current execution is not asserted.';}
  if (failed) {pill='Refresh unavailable';activity='Could not refresh; showing the last published snapshot. Current execution is not asserted.';}
  return {pill,activity,stale,
    validation:s.collection_complete ? 'Review pending' : s.state === 'UNKNOWN' ? 'Unknown' : failed || stale ? 'Needs fresh observation' : periodic ? 'In progress · not scored' : 'Incomplete',
    note:`${s.run_label}. Private observations are scheduled every 15 minutes while the local observer is available; publishing adds deployment delay. The page checks published JSON every 30 seconds. A snapshot expires after 20 minutes while active. Refresh never starts or resumes validation.`,
    next:s.collection_complete ? 'Verify final restoration and artifact custody, then score the matched heldout and regression comparisons and review errors. Only evidence from that review can establish whether the adapter helps.' : s.state === 'INCOMPLETE_STOPPED' ? 'Investigate the stop cause, verify restoration and preserve the stopped evidence. Any new attempt requires separate authorization. Then complete and score the matched comparisons.' : 'Finish the current fresh validation attempt, verify process exit, exact reservation release and artifact custody, then score the matched heldout and regression comparisons and review errors.'};
}
