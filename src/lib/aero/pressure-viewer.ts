import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

export interface PressureSurface {
  schema: 'aero.scientific.surface.v1';
  field: 'p' | 'DISPLACEMENT' | 'VON_MISES' | 'MAX_PRINCIPAL' | 'MIN_PRINCIPAL' | 'TEMPERATURE';
  label: string;
  units: 'Pa' | 'm' | 'K';
  provenance: 'SOLVER_OUTPUT';
  artifactSha256: string;
  positions: number[];
  triangles: number[];
  pointScalars: number[];
  range: [number, number];
  fields?: Record<string, {units: string; values: number[]; provenance?: string}>;
  displacements?: number[];
  mesh: { points: number; volumeCells: number; boundaryFaces: number };
}

export interface PressureViewer {
  resetCamera(): void;
  zoom(factor: number): void;
  setMeshVisible(visible: boolean): void;
  setDeformationScale(scale: number): void;
  setField(field: string): {low:number; high:number; units:string};
  dispose(): void;
}

function scalarColor(value: number, low: number, high: number): THREE.Color {
  const span = high - low;
  const t = span > 0 ? Math.min(1, Math.max(0, (value - low) / span)) : 0.5;
  const stops = [
    new THREE.Color('#173f4b'),
    new THREE.Color('#4f7f79'),
    new THREE.Color('#d9c89d'),
    new THREE.Color('#d7653f'),
  ];
  const scaled = t * (stops.length - 1);
  const index = Math.min(stops.length - 2, Math.floor(scaled));
  return stops[index].clone().lerp(stops[index + 1], scaled - index);
}

export function mountPressureViewer(container: HTMLElement, surface: PressureSurface, options: { autoRotate?: boolean; meshOnly?: boolean } = {}): PressureViewer {
  if (surface.schema !== 'aero.scientific.surface.v1' || !['p','DISPLACEMENT','VON_MISES','MAX_PRINCIPAL','MIN_PRINCIPAL','TEMPERATURE'].includes(surface.field)) {
    throw new Error('Unsupported scientific surface contract');
  }
  if (surface.positions.length !== surface.pointScalars.length * 3) {
    throw new Error('Pressure surface point/scalar counts do not match');
  }
  if (!surface.positions.every(Number.isFinite) || !surface.pointScalars.every(Number.isFinite) || !surface.triangles.every(i => Number.isInteger(i) && i >= 0 && i < surface.pointScalars.length)) throw new Error('Invalid scientific mesh data');

  container.replaceChildren();
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#111719');
  const camera = new THREE.PerspectiveCamera(34, 1, 1e-5, 100);
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  container.appendChild(renderer.domElement);

  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.Float32BufferAttribute(surface.positions, 3));
  geometry.setIndex(surface.triangles);
  const [low, high] = surface.range;
  const colors: number[] = [];
  for (const scalar of surface.pointScalars) {
    const color = scalarColor(scalar, low, high);
    colors.push(color.r, color.g, color.b);
  }
  geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
  geometry.computeVertexNormals();
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();

  const surfaceMesh = new THREE.Mesh(
    geometry,
    new THREE.MeshStandardMaterial({
      vertexColors: !options.meshOnly, color: options.meshOnly ? '#244650' : '#ffffff', roughness: 0.82, metalness: 0.02, side: THREE.DoubleSide,
    }),
  );
  const wireframe = new THREE.LineSegments(
    new THREE.WireframeGeometry(geometry),
    new THREE.LineBasicMaterial({ color: '#94dadb', transparent: true, opacity: options.meshOnly ? 0.65 : 0.16 }),
  );
  wireframe.visible = Boolean(options.meshOnly);
  scene.add(surfaceMesh, wireframe);
  scene.add(new THREE.HemisphereLight('#f0ece1', '#1b2528', 2.2));
  const key = new THREE.DirectionalLight('#ffffff', 1.5);
  key.position.set(1, 1.5, 2);
  scene.add(key);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.screenSpacePanning = true;
  controls.autoRotate = Boolean(options.autoRotate);
  controls.autoRotateSpeed = 0.5;

  const resetCamera = () => {
    const box = geometry.boundingBox;
    const sphere = geometry.boundingSphere;
    if (!box || !sphere) return;
    const size = box.getSize(new THREE.Vector3());
    const radius = Math.max(sphere.radius, 1e-3);
    const verticalFov = THREE.MathUtils.degToRad(camera.fov);
    const fittedSpan = Math.max(size.y, size.x / Math.max(camera.aspect, 0.1));
    const distance = Math.max(radius * 1.2, (fittedSpan / (2 * Math.tan(verticalFov / 2))) * 1.25);
    controls.target.copy(sphere.center);
    // The nozzle axis is X and the one-degree wedge is nearly flat in Z. Look
    // predominantly along Z so the engineering profile is visible by default.
    camera.position.copy(sphere.center).add(new THREE.Vector3(0, distance * 0.12, distance));
    camera.near = Math.max(distance / 1000, 1e-6);
    camera.far = distance * 100;
    camera.updateProjectionMatrix();
    controls.update();
  };
  resetCamera();

  let frame = 0;
  const render = () => {
    controls.update();
    renderer.render(scene, camera);
    frame = requestAnimationFrame(render);
  };
  render();

  const resize = () => {
    const width = Math.max(1, container.clientWidth);
    const height = Math.max(1, container.clientHeight);
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  };
  const observer = new ResizeObserver(resize);
  observer.observe(container);
  resize();
  resetCamera();

  return {
    resetCamera,
    zoom(factor: number) {
      if (!Number.isFinite(factor) || factor <= 0) return;
      camera.position.sub(controls.target).multiplyScalar(1 / factor).add(controls.target);
      controls.update();
    },
    setMeshVisible(visible: boolean) { wireframe.visible = visible; },
    setDeformationScale(scale: number) {
      if (!Number.isFinite(scale) || scale < 0 || scale > 1000) throw new Error('Deformation scale must be 0–1000');
      if (!surface.displacements || surface.displacements.length !== surface.positions.length || !surface.displacements.every(Number.isFinite)) throw new Error('Measured displacement field unavailable');
      const coordinates = surface.positions.map((x,i) => x + scale * surface.displacements![i]);
      geometry.setAttribute('position', new THREE.Float32BufferAttribute(coordinates, 3));
      geometry.computeVertexNormals(); geometry.computeBoundingBox(); geometry.computeBoundingSphere();
      wireframe.geometry.dispose(); wireframe.geometry = new THREE.WireframeGeometry(geometry);
    },
    setField(field: string) {
      const selected = surface.fields?.[field];
      if (!selected || selected.values.length !== surface.pointScalars.length || !selected.values.every(Number.isFinite)) throw new Error('Measured field unavailable');
      const low = Math.min(...selected.values), high = Math.max(...selected.values);
      const colors = selected.values.flatMap(value => { const c = scalarColor(value,low,high); return [c.r,c.g,c.b]; });
      geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors,3));
      return {low,high,units:selected.units};
    },
    dispose() {
      cancelAnimationFrame(frame);
      observer.disconnect();
      controls.dispose();
      geometry.dispose();
      (surfaceMesh.material as THREE.Material).dispose();
      wireframe.geometry.dispose();
      (wireframe.material as THREE.Material).dispose();
      renderer.dispose();
      container.replaceChildren();
    },
  };
}
