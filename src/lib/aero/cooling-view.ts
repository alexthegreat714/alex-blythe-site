import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
export function coolingGeometry(host:HTMLElement,lengthMm:number,count:number,diameterMm:number){
  host.replaceChildren();const scene=new THREE.Scene();scene.background=new THREE.Color('#0e1a23');const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));host.append(renderer.domElement);
  const length=lengthMm/1000,d=diameterMm/1000*15,spacing=(diameterMm+1)/1000*15;
  for(let i=0;i<count;i++){const mesh=new THREE.Mesh(new THREE.CylinderGeometry(d/2,d/2,length,48),new THREE.MeshStandardMaterial({color:'#65bfca',metalness:.3,roughness:.35}));mesh.rotation.z=Math.PI/2;mesh.position.set(0,(i-(count-1)/2)*spacing,0);scene.add(mesh);}
  const camera=new THREE.PerspectiveCamera(38,1,.001,10);camera.position.set(length*.7,length*.7,length*1.25);const controls=new OrbitControls(camera,renderer.domElement);controls.update();scene.add(new THREE.HemisphereLight(0xffffff,0x263542,2));const light=new THREE.DirectionalLight(0xffffff,2);light.position.set(1,1,1);scene.add(light);
  function render(){const w=host.clientWidth||500,h=host.clientHeight||320;renderer.setSize(w,h,false);camera.aspect=w/h;camera.updateProjectionMatrix();renderer.render(scene,camera);}controls.addEventListener('change',render);const observer=new ResizeObserver(render);observer.observe(host);render();
  return ()=>{observer.disconnect();controls.dispose();scene.traverse(o=>{const m=o as THREE.Mesh;m.geometry?.dispose();if(m.material)(Array.isArray(m.material)?m.material:[m.material]).forEach(x=>x.dispose());});renderer.dispose();host.replaceChildren();};
}
