export type SoftwareArtifact = {
  label: string;
  description: string;
  href?: string;
};

export type SoftwareProject = {
  slug: 'aero' | 'forgeclaw' | 'ocr97';
  name: string;
  category: string;
  status: string;
  year: string;
  version?: string;
  summary: string;
  purpose: string;
  keyIdeas: string[];
  problem: string[];
  designApproach: string[];
  boundaries: string[];
  evidence: string[];
  limitations: string[];
  artifacts: SoftwareArtifact[];
  repository?: string;
  relatedResearch?: { label: string; href: string };
};

export const softwareProjects: SoftwareProject[] = [
  {
    slug: 'aero',
    name: 'Aero',
    category: 'Engineering orchestration / CFD',
    status: 'Public beta / preliminary analysis',
    year: '2026',
    summary: 'Turn an engineering question into a reviewable CFD study: requirements, first-principles checks, design comparisons and OpenFOAM evidence.',
    purpose: 'Aero connects engineering problem framing, fidelity selection, solver setup, execution evidence, and review without treating an AI-generated answer as computational authority.',
    keyIdeas: [
      'Engineering problem framing and fidelity selection',
      'Geometry, mesh, boundary-condition, and preflight checks',
      'Convergence, conservation, and validation gates',
      'Linux-native OpenFOAM execution',
      'Python analysis and inspectable run artifacts',
    ],
    problem: [
      'CFD work is not one calculation. It is a chain of assumptions, setup decisions, solver behavior, numerical checks, and interpretation that can fail at different points.',
      'Aero is being developed to make that chain explicit and reviewable while helping an engineer move between first-order estimates and higher-fidelity numerical work.',
    ],
    designApproach: [
      'A typed, versioned case specification carries geometry, mesh, material, model, boundary-condition, and run intent into the workflow.',
      'Static and live preflight checks inspect the case before execution. Telemetry and bounded numerical adjustments support supervised runs rather than open-ended solver control.',
      'Artifacts, manifests, convergence history, conservation checks, and validation status remain attached to the result so the reasoning can be inspected after execution.',
    ],
    boundaries: [
      'The numerical solver—not the AI—is the computational authority.',
      'Aero does not treat a converged solution as a validated prediction.',
      'Consequential setup changes and engineering conclusions remain subject to human review.',
      'A bounded solver smoke test proves an execution path, not design fitness or predictive validity.',
    ],
    evidence: [
      'The OpenFOAM path produces case specifications, preflight results, run telemetry, and evidence manifests for review.',
      'Recorded OpenFOAM examples retain mesh-refinement comparisons, convergence charts, and rendered pressure fields.',
      'Promotion toward engineering evidence requires numerical convergence, conservation checks, and comparison with an appropriate analytical, experimental, or reference basis.',
    ],
    limitations: [
      'The public release supports preliminary analysis with explicit physical assumptions and numerical checks.',
      'Visitors can run a bounded parallel-plate channel study. General CAD uploads and arbitrary solver cases use the private workspace.',
      'Validation coverage depends on the problem class; completed execution alone does not establish physical accuracy.',
    ],
    artifacts: [
      { label: 'CFD technical article', description: 'Background on CFD foundations, workflow, and aerospace applications.', href: '/2023/12/28/mastering-computational-fluid-dynamics-cfd-for-aerospace-engineering-a-journey-to-proficiency/' },
      { label: 'Case specifications', description: 'Typed inputs that keep setup intent and solver configuration inspectable.', href: '/software/aero/current/' },
      { label: 'Run evidence', description: 'Preflight results, telemetry, manifests, and validation status retained with each workflow.', href: '/software/aero/evidence/' },
    ],
  },
  {
    slug: 'forgeclaw',
    name: 'ForgeClaw',
    category: 'Bounded agent execution',
    status: 'Alpha / experimental',
    year: '2026',
    version: 'v0.1.0-alpha.6',
    summary: 'A framework for supervised agent execution with explicit authority boundaries, observable tool handoffs, evidence capture, verification, and controlled escalation.',
    purpose: 'ForgeClaw explores how an agent can act on a declared surface, preserve what happened, and require separate evidence before a result is accepted.',
    keyIdeas: [
      'Declared execution surfaces and explicit tool authority',
      'Bounded action loops with policy checks',
      'Evidence capture and concrete failure classification',
      'Acceptance criteria separated from execution success',
      'Human review and controlled escalation',
    ],
    problem: [
      'A tool call can return successfully while the actual task remains incomplete, incorrect, or unproven.',
      'ForgeClaw addresses that gap by separating intent, execution, and verification and by keeping the operating boundary visible throughout the run.',
    ],
    designApproach: [
      'Each session declares its execution surface, objective, permitted actions, and stop conditions before mutation occurs.',
      'The controller observes, plans, performs one bounded action, records the result, then verifies the observed state against acceptance criteria.',
      'Structured failure classes preserve useful evidence when a target is unavailable, a surface is unknown, approval is missing, or human review is required.',
    ],
    boundaries: [
      'Successful tool execution does not automatically mean the result passed verification.',
      'Unknown surfaces fail closed, and native desktop control is treated as elevated risk and disabled by default.',
      'ForgeClaw is not a security sandbox, an autonomous correctness guarantee, or permission to expand beyond the declared objective.',
    ],
    evidence: [
      'Lifecycle artifacts retain requested intent, observed state, action results, expected state, and the verification verdict.',
      'A public contract-only example demonstrates a no-mutation run where execution completed but acceptance remained unproven and the result was rejected.',
      'Browser and workflow checks can test URLs, visible text, field values, controls, artifacts, and combined acceptance conditions.',
    ],
    limitations: [
      'Visual perception and OCR can misread a target, and weak acceptance criteria can produce weak verification.',
      'The current lifecycle coordinates separated phases within one controller; it does not claim process-level or security-principal isolation.',
      'Native desktop automation remains elevated risk and requires deliberate enablement and supervision.',
    ],
    artifacts: [
      { label: 'Repository', description: 'Public source, safety model, lifecycle controller, and examples.', href: 'https://github.com/PrecisionArtsLab/ForgeClaw' },
      { label: 'Architecture note', description: 'Why intent, execution, and verification carry different authority.', href: '/software/notes/separating-intent-execution-verification/' },
      { label: 'Verification evidence', description: 'Inspectable pass/fail records designed to preserve the reason a result was accepted or rejected.' },
    ],
    repository: 'https://github.com/PrecisionArtsLab/ForgeClaw',
    relatedResearch: { label: 'Separating Intent, Execution, and Verification', href: '/software/notes/separating-intent-execution-verification/' },
  },
  {
    slug: 'ocr97',
    name: 'OCR97',
    category: 'Evidence-aware document processing',
    status: 'Alpha / experimental',
    year: '2026',
    version: 'v0.1.0-alpha',
    summary: 'A local document and image-text processing tool for screenshots, scans, forms, and image-based PDFs with adaptive preprocessing, lane selection, uncertainty visibility, and inspectable output.',
    purpose: 'OCR97 treats extracted text as evidence with provenance and uncertainty rather than as a guaranteed transcription ready for silent downstream use.',
    keyIdeas: [
      'Native PDF text and local OCR routing',
      'Adaptive image preprocessing',
      'Screenshots, scans, forms, and image-based PDFs',
      'Confidence and uncertainty visibility',
      'Source preservation and downstream verification',
    ],
    problem: [
      'Document automation often passes OCR output downstream without preserving the source image, routing decision, or uncertainty that produced it.',
      'OCR97 is designed to keep those decisions inspectable so a workflow can distinguish usable extraction from partial or failed evidence.',
    ],
    designApproach: [
      'The pipeline selects between native PDF text and local OCR engines, applies preprocessing where appropriate, and retains source evidence with the result.',
      'Routing and scoring expose which extraction lane was used and where confidence is limited instead of presenting every output as equally reliable.',
      'CLI and gateway interfaces support repeatable local workflows without requiring document content to be sent to a hosted OCR service.',
    ],
    boundaries: [
      'OCR97 does not claim universal character or document accuracy.',
      'Confidence scores and benchmark results are evidence about a specific dataset, configuration, and scoring method—not proof for every document type.',
      'Low-quality scans and handwriting require review; downstream systems should not treat uncertain text as authoritative.',
    ],
    evidence: [
      'A corrected public SROIE receipt-field run scored 92/100 across the first 50 evaluated receipts using the project-specific field metric.',
      'That bounded result trailed the referenced docTR result of 96.5 and exceeded the referenced Tesseract result of 80 under the documented comparison; it is not a universal accuracy percentage.',
      'A two-line IAM handwriting check scored 28.5/100, a deliberately visible weak result from a sample too small for broad conclusions.',
    ],
    limitations: [
      'Handwriting performance is weak in the current evidence and needs broader evaluation.',
      'The published samples are bounded and do not establish production reliability across arbitrary document classes.',
      'Local preprocessing and OCR can have high latency, especially on difficult or multi-page inputs.',
    ],
    artifacts: [
      { label: 'Repository', description: 'Public source, setup notes, benchmark definitions, and roadmap.', href: 'https://github.com/PrecisionArtsLab/ocr97' },
      { label: 'Benchmark notes', description: 'Dataset scope, scoring method, and bounded comparison results.', href: 'https://github.com/PrecisionArtsLab/ocr97/blob/main/docs/BENCHMARKS.md' },
      { label: 'Inspectable output', description: 'Extraction results retain routing, evidence, and uncertainty for downstream review.' },
    ],
    repository: 'https://github.com/PrecisionArtsLab/ocr97',
  },
];

export const softwareBySlug = Object.fromEntries(softwareProjects.map((project) => [project.slug, project])) as Record<SoftwareProject['slug'], SoftwareProject>;
