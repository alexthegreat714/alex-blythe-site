import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { STLLoader } from 'three/addons/loaders/STLLoader.js';

export interface CadViewer {
  resetCamera(): void;
  setMeshVisible(visible: boolean): void;
  dispose(): void;
}

export function mountCadViewer(container: HTMLElement, payload: ArrayBuffer): CadViewer {
  const geometry = new STLLoader().parse(payload);
  if (!geometry.getAttribute('position') || geometry.getAttribute('position').count < 3) {
    geometry.dispose();
    throw new Error('Generated STL contains no renderable surface');
  }
  geometry.computeVertexNormals();
  geometry.computeBoundingBox();
  geometry.computeBoundingSphere();

  container.replaceChildren();
  const scene = new THREE.Scene();
  scene.background = new THREE.Color('#111719');
  const camera = new THREE.PerspectiveCamera(34, 1, 1e-4, 100000);
  const renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  container.appendChild(renderer.domElement);

  const surface = new THREE.Mesh(
    geometry,
    new THREE.MeshStandardMaterial({ color: '#d8cda9', roughness: 0.8, metalness: 0.03 }),
  );
  const wireframe = new THREE.LineSegments(
    new THREE.WireframeGeometry(geometry),
    new THREE.LineBasicMaterial({ color: '#d7653f', transparent: true, opacity: 0.2 }),
  );
  wireframe.visible = false;
  scene.add(surface, wireframe);
  scene.add(new THREE.HemisphereLight('#f0ece1', '#1b2528', 2.2));
  const key = new THREE.DirectionalLight('#ffffff', 1.4);
  key.position.set(1, 1.5, 2);
  scene.add(key);

  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.screenSpacePanning = true;

  const resetCamera = () => {
    const sphere = geometry.boundingSphere;
    if (!sphere) return;
    const radius = Math.max(sphere.radius, 1e-3);
    controls.target.copy(sphere.center);
    camera.position.copy(sphere.center).add(new THREE.Vector3(radius * 1.8, radius * 1.25, radius * 2.1));
    camera.near = radius / 100;
    camera.far = radius * 100;
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

  return {
    resetCamera,
    setMeshVisible(visible: boolean) { wireframe.visible = visible; },
    dispose() {
      cancelAnimationFrame(frame);
      observer.disconnect();
      controls.dispose();
      geometry.dispose();
      (surface.material as THREE.Material).dispose();
      wireframe.geometry.dispose();
      (wireframe.material as THREE.Material).dispose();
      renderer.dispose();
      container.replaceChildren();
    },
  };
}
