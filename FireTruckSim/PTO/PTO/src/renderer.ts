import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";

// Types for preload API
declare global {
  interface Window {
    api: {
      sendUDP: (data: Record<string, number>) => void;
      onPTOUpdate: (callback: (value: number) => void) => void;
    };
  }
}

let ptoEngaged = false;
let ledMesh: THREE.Mesh | undefined;
let leverParts: THREE.Mesh[] = [];
let offLeverPosition = Math.PI * .2;
let onLeverPosition = Math.PI * .7;

// LED On material
const ledOnMaterial = new THREE.MeshPhysicalMaterial({
  color: 0x00ff00,
  roughness: 0.1,       
  metalness: 0.5,       
  reflectivity: 0.8,    
  clearcoat: 1.0,      
  clearcoatRoughness: 0.05,
});

// LED Off material
const ledOffMaterial = new THREE.MeshPhysicalMaterial({
  color: 0x0c2e08,
  roughness: 0.3,
  metalness: 0.2,
  reflectivity: 0.8,
  clearcoat: 1.0,
  clearcoatRoughness: 0.1,
});

// Scene setup
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x272727);

const camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 0, 0);

const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const dirLight = new THREE.DirectionalLight(0xffffff, 3);
dirLight.position.set(5, 5, 5);
scene.add(dirLight);
scene.add(new THREE.AmbientLight(0x404040, 8));

// Load ptoModel
const loader = new GLTFLoader();
loader.load("models/PTO.glb", (gltf) => {
  const ptoModel = gltf.scene;
  scene.add(ptoModel);

  ptoModel.position.set(0, 0, 0);
  ptoModel.rotation.set(0, -1.0, 0);
  ptoModel.scale.set(1, 1, 1);

  // Camera setup based on ptoModel bounds
  const box = new THREE.Box3().setFromObject(ptoModel);
  const center = new THREE.Vector3();
  box.getCenter(center);
  camera.position.set(1, center.y, 4);
  camera.lookAt(center);
  camera.position.y += .3;
  camera.updateProjectionMatrix();

  // Find LED mesh and set initial material
  ptoModel.traverse((child) => {
    if (child instanceof THREE.Mesh && child.name === "LED") {
      ledMesh = child;
      ledMesh.material = ledOffMaterial;
      ledMesh.userData.clickable = true;
    } else if (child instanceof THREE.Mesh) {
      child.userData.clickable = true;
    }
  });

  // Lever is in three parts, there were problems with muliple materials on one mesh
  // Grab all lever parts and set them to their inital off position
  ptoModel.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      console.log(child.name);
      if (child.name === "Yellow_Grip" || child.name === "Shaft" || child.name === "Knob") {
        leverParts.push(child);
        child.rotation.z = offLeverPosition;
      }
    }
  });

  // On click to move lever and change PTO state
  const raycaster = new THREE.Raycaster();
  const mouse = new THREE.Vector2();
  window.addEventListener("click", (event) => {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(scene.children, true);
    for (const hit of intersects) {
      if (hit.object.userData.clickable) {
        ptoEngaged = !ptoEngaged;
        window.api.sendUDP({ pto: ptoEngaged ? 1.0 : 0.0 });
        leverParts.forEach((part) => {
          part.rotation.z = ptoEngaged ? onLeverPosition : offLeverPosition;
        })
        break;
      }
    }
  });

});

// Handle UDP update
window.api.onPTOUpdate((value: number) => {
  ptoEngaged = value === 1.0;
  if (ledMesh) {
    ledMesh.material = ptoEngaged ? ledOnMaterial : ledOffMaterial;
    ledMesh.material.needsUpdate = true;
  }
});

// Resize handling
window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});



// Animation loop
function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}
animate();
