import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';

export function channelView(host:HTMLElement, length:number, gap:number, nx:number, ny:number, mode:number, values?:number[]) {
  host.replaceChildren();
  const scene=new THREE.Scene();scene.background=new THREE.Color('#0e1a23');
  const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));host.append(renderer.domElement);
  const camera=new THREE.PerspectiveCamera(38,1,.0001,10);camera.position.set(length*.55,length*.65,length*1.1);
  const controls=new OrbitControls(camera,renderer.domElement);controls.target.set(length/2,gap*10,0);controls.update();
  const h=gap*20,z=.001*20;
  const block=new THREE.BoxGeometry(length,h,z);
  const material=new THREE.MeshStandardMaterial({color:'#87bac4',transparent:true,opacity:mode===2?.8:.12,roughness:.45,metalness:.2});
  const box=new THREE.Mesh(block,material);box.position.set(length/2,h/2,-z/2);scene.add(box);
  const edges=new THREE.LineSegments(new THREE.EdgesGeometry(block),new THREE.LineBasicMaterial({color:'#82b7c2'}));edges.position.copy(box.position);scene.add(edges);
  if(mode===3){
    const points:number[]=[];
    for(let x=0;x<=nx;x++)points.push(x*length/nx,0,.00002,x*length/nx,h,.00002);
    for(let y=0;y<=ny;y++)points.push(0,y*h/ny,.00002,length,y*h/ny,.00002);
    const lines=new THREE.BufferGeometry();lines.setAttribute('position',new THREE.Float32BufferAttribute(points,3));
    scene.add(new THREE.LineSegments(lines,new THREE.LineBasicMaterial({color:'#64d4d1'})));
  }
  if(mode===5&&values?.length===nx*ny){
    const positions:number[]=[],colors:number[]=[];const lo=Math.min(...values),hi=Math.max(...values),color=new THREE.Color();
    for(let y=0;y<ny;y++)for(let x=0;x<nx;x++){
      const x0=x*length/nx,x1=(x+1)*length/nx,y0=y*h/ny,y1=(y+1)*h/ny;
      positions.push(x0,y0,.00004,x1,y0,.00004,x1,y1,.00004,x0,y0,.00004,x1,y1,.00004,x0,y1,.00004);
      color.setHSL(.65*(1-(values[y*nx+x]-lo)/(hi-lo||1)),.78,.54);
      for(let i=0;i<6;i++)colors.push(color.r,color.g,color.b);
    }
    const geometry=new THREE.BufferGeometry();geometry.setAttribute('position',new THREE.Float32BufferAttribute(positions,3));geometry.setAttribute('color',new THREE.Float32BufferAttribute(colors,3));
    scene.add(new THREE.Mesh(geometry,new THREE.MeshBasicMaterial({vertexColors:true,side:THREE.DoubleSide})));
  }
  scene.add(new THREE.HemisphereLight(0xffffff,0x263542,2));const light=new THREE.DirectionalLight(0xffffff,2);light.position.set(1,1,1);scene.add(light);
  const resize=()=>{const w=host.clientWidth||500,height=host.clientHeight||270;renderer.setSize(w,height,false);camera.aspect=w/height;camera.updateProjectionMatrix();renderer.render(scene,camera);};
  controls.addEventListener('change',resize);const observer=new ResizeObserver(resize);observer.observe(host);resize();
  return ()=>{observer.disconnect();controls.dispose();scene.traverse(o=>{const mesh=o as THREE.Mesh;if(mesh.geometry)mesh.geometry.dispose();if(mesh.material)(Array.isArray(mesh.material)?mesh.material:[mesh.material]).forEach(m=>m.dispose());});renderer.dispose();host.replaceChildren();};
}
