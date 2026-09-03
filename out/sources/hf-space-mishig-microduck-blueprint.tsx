'use client';

import { useEffect, useRef, useState } from 'react';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { ScanSearch } from 'lucide-react';
import * as THREE from 'three';

import {
  MICRODUCK_JOINT_ORDER,
  MICRODUCK_TRUNK_HEIGHT,
  MICRODUCK_TRUNK_LATERAL,
  MICRODUCK_TRUNK_PITCH,
  MICRODUCK_TRUNK_ROLL,
  MICRODUCK_WALK_CHANNELS,
  MICRODUCK_WALK_CYCLE_SECONDS,
  MICRODUCK_WALK_FRAMES,
} from '@/lib/microduck-walk-trajectory';

type LayerPreset = 'ALL' | 'MOTORS' | 'SENSORS' | 'CORE' | 'POWER';
type PartCategory = 'shell' | 'motor' | 'sensor' | 'compute' | 'power' | 'structure';

type FocusStage = {
  id: LayerPreset;
  number: string;
  label: string;
  detail: string;
  sticker: string;
  target: [number, number, number];
  cameraOffset: [number, number, number];
  zoom: number;
  explosion: number;
};

type Inspection = {
  name: string;
  eyebrow: string;
  detail: string;
  confidence: string;
  x: number;
  y: number;
};

type Telemetry = {
  phase: number;
  hip: number;
  tilt: number;
};

type KinematicGeom = {
  mesh?: string;
  pos?: [number, number, number];
  quat?: [number, number, number, number];
  color?: [number, number, number, number];
};

type KinematicBody = {
  name: string;
  parent?: string | null;
  pos: [number, number, number];
  quat: [number, number, number, number];
  joint?: {
    name: string;
    axis: [number, number, number];
    type?: string;
    range?: [number, number];
  } | null;
  geoms: KinematicGeom[];
};

type Kinematics = { bodies: KinematicBody[] };

type JointRig = {
  name: string;
  body: THREE.Group;
  baseQuaternion: THREE.Quaternion;
  axis: THREE.Vector3;
  min: number;
  max: number;
  gaitAngle: number;
  ikOffset: number;
  currentAngle: number;
};

type IKChainId = 'left-leg' | 'right-leg' | 'head';

type IKChainSpec = {
  id: IKChainId;
  bodies: readonly string[];
};

type IKInteraction = {
  pointerId: number;
  part: Explodable;
  chain: IKChainSpec;
  joints: JointRig[];
  effector: THREE.Object3D;
  effectorLocal: THREE.Vector3;
  plane: THREE.Plane;
  target: THREE.Vector3;
};

type IKHit = {
  part: Explodable;
  chain: IKChainSpec;
  joints: JointRig[];
  effector: THREE.Object3D;
  effectorLocal: THREE.Vector3;
  point: THREE.Vector3;
};

type Explodable = {
  mesh: THREE.Mesh<THREE.BufferGeometry, THREE.ShaderMaterial>;
  outline: THREE.LineBasicMaterial;
  base: THREE.Vector3;
  baseColor: THREE.Color;
  vector: THREE.Vector3;
  assemblyVector: THREE.Vector3;
  assemblyArc: THREE.Vector3;
  assemblyDelay: number;
  shell: boolean;
  category: PartCategory;
};

type BeakPart = {
  mesh: THREE.Mesh<THREE.BufferGeometry, THREE.ShaderMaterial>;
  basePosition: THREE.Vector3;
  baseQuaternion: THREE.Quaternion;
  pivot: THREE.Vector3;
  axis: THREE.Vector3;
};

type SceneApi = {
  focusStage: (index: number) => void;
};

const INTERNAL_MARKERS = [
  'xl330',
  'pcb',
  'np_f',
  'speaker',
  'bearing',
  'motor_support',
  'power_support',
  'lens',
];

const IK_CHAINS: Record<IKChainId, IKChainSpec> = {
  'left-leg': {
    id: 'left-leg',
    bodies: ['yaw2roll', 'hip_l', 'upper_leg_left', 'leg', 'ankle_left'],
  },
  'right-leg': {
    id: 'right-leg',
    bodies: ['bearing_roll', 'hip_l_2', 'upper_leg_right', 'leg_2', 'ankle_right'],
  },
  head: {
    id: 'head',
    bodies: ['neck', 'neck_pitch', 'yaw_roll_motion', 'jaw_soft'],
  },
};

const LAYERS: FocusStage[] = [
  {
    id: 'ALL',
    number: '01',
    label: 'ENTIRE RIG',
    detail: 'Complete walking assembly · official simulator geometry',
    sticker: '/stickers/quack.png',
    target: [0.005, 0.142, 0],
    cameraOffset: [0.39, 0.155, 0.42],
    zoom: 1.1,
    explosion: 0,
  },
  {
    id: 'MOTORS',
    number: '02',
    label: 'SMART SERVOS',
    detail: '15 joint-mounted XL330-class actuator volumes across the kinematic chain',
    sticker: '/stickers/bolt-teal.png',
    target: [0.004, 0.14, 0],
    cameraOffset: [0.39, 0.155, 0.42],
    zoom: 1.2,
    explosion: 0.42,
  },
  {
    id: 'SENSORS',
    number: '03',
    label: 'VISION + RANGE',
    detail: 'Head camera, optical envelope and 8×8 time-of-flight range system',
    sticker: '/stickers/shooting-star.png',
    target: [0.036, 0.29, 0],
    cameraOffset: [0.52, 0.015, 0.001],
    zoom: 1.82,
    explosion: 0.72,
  },
  {
    id: 'CORE',
    number: '04',
    label: 'COMPUTE + I/O',
    detail: 'Radxa compute envelope, Robot HAT, audio and peripheral interfaces',
    sticker: '/stickers/burst-blue.png',
    target: [0.064, 0.328, -0.014],
    cameraOffset: [0.46, 0.065, -0.24],
    zoom: 2.05,
    explosion: 0.76,
  },
  {
    id: 'POWER',
    number: '05',
    label: 'POWER + FRAME',
    detail: 'Removable battery, bearing stack and load-bearing internal structure',
    sticker: '/stickers/flame-orange-2.png',
    target: [-0.018, 0.128, 0],
    cameraOffset: [0.001, 0.035, 0.52],
    zoom: 1.62,
    explosion: 0.68,
  },
];

const CATEGORY_COLORS: Record<PartCategory, number> = {
  shell: 0xa3a2a0,
  motor: 0xe8407f,
  sensor: 0x0bbac6,
  compute: 0x8b70cf,
  power: 0xf09a5e,
  structure: 0x888a8e,
};

const vertexShader = /* glsl */ `
  varying vec3 vNormal;
  varying vec3 vViewDirection;
  varying vec3 vWorldPosition;

  void main() {
    vec4 world = modelMatrix * vec4(position, 1.0);
    vec4 view = viewMatrix * world;
    vNormal = normalize(normalMatrix * normal);
    vViewDirection = normalize(-view.xyz);
    vWorldPosition = world.xyz;
    gl_Position = projectionMatrix * view;
  }
`;

const fragmentShader = /* glsl */ `
  uniform vec3 uColor;
  uniform vec3 uInk;
  uniform float uOpacity;
  varying vec3 vNormal;
  varying vec3 vViewDirection;
  varying vec3 vWorldPosition;

  void main() {
    float facing = abs(dot(normalize(vNormal), normalize(vViewDirection)));
    float rim = 1.0 - clamp(facing, 0.0, 1.0);
    float diffuse = max(dot(normalize(vNormal), normalize(vec3(0.32, 0.76, 0.56))), 0.0);
    float hatchA = smoothstep(0.9, 1.0, 0.5 + 0.5 * sin((vWorldPosition.x + vWorldPosition.y) * 245.0));
    float hatchB = smoothstep(0.93, 1.0, 0.5 + 0.5 * sin((vWorldPosition.z - vWorldPosition.y) * 285.0));
    float grain = 0.5 + 0.5 * sin(gl_FragCoord.x * 0.73 + gl_FragCoord.y * 1.17);
    vec3 pencil = mix(uInk, uColor, 0.66 + diffuse * 0.18);
    pencil *= 0.93 + diffuse * 0.055 + grain * 0.015;
    pencil = mix(pencil, uInk, rim * 0.065 + (hatchA + hatchB) * 0.022);
    float alpha = uOpacity * (0.58 + rim * 0.12);
    gl_FragColor = vec4(pencil, clamp(alpha, 0.0, 0.48));
  }
`;

function quaternionFromMjcf(quat: [number, number, number, number]) {
  return new THREE.Quaternion(quat[1], quat[2], quat[3], quat[0]);
}

function isInternal(meshName: string) {
  return INTERNAL_MARKERS.some((marker) => meshName.toLowerCase().includes(marker));
}

function categoryFor(meshName: string): PartCategory {
  const name = meshName.toLowerCase();
  if (name.includes('xl330')) return 'motor';
  if (name.includes('np_f') || name.includes('power_support') || name.includes('banana_pcb')) {
    return 'power';
  }
  if (name.includes('pcb') || name.includes('robot_hat')) return 'compute';
  if (
    name.includes('lens') ||
    name.includes('face_part') ||
    name.includes('noenoeil') ||
    name.includes('speaker')
  ) {
    return 'sensor';
  }
  if (
    name.includes('shell') ||
    name.includes('jaw') ||
    name.includes('mouth') ||
    name.includes('foot') ||
    name.includes('sole') ||
    name.includes('upper_leg')
  ) {
    return 'shell';
  }
  return 'structure';
}

function layerMatches(layer: LayerPreset, category: PartCategory) {
  if (layer === 'ALL') return true;
  if (layer === 'MOTORS') return category === 'motor';
  if (layer === 'SENSORS') return category === 'sensor';
  if (layer === 'CORE') return category === 'compute';
  return category === 'power';
}

function layerVisibilityWeight(layer: LayerPreset, category: PartCategory) {
  if (layer === 'ALL' || layerMatches(layer, category)) return 1;
  if (layer === 'POWER' && category === 'structure') return 0.28;
  if (category === 'structure') return 0.065;
  if (category === 'shell') return 0.025;
  return 0.018;
}

function ikChainForPart(part: Explodable): IKChainSpec | null {
  const explicitChain = part.mesh.userData.ikChainId as IKChainId | undefined;
  if (explicitChain) return IK_CHAINS[explicitChain];

  const bodyName = part.mesh.userData.bodyName as string | undefined;
  if (!bodyName) return null;
  for (const chain of Object.values(IK_CHAINS)) {
    if (chain.bodies.includes(bodyName)) return chain;
  }
  return null;
}

function inspectionCopy(meshName: string, category: PartCategory) {
  const name = meshName.toLowerCase();
  if (name.includes('xl330')) {
    return {
      name: 'DYNAMIXEL XL330',
      eyebrow: 'SMART SERVO / 1 OF 15',
      detail: '20 × 34 × 26 mm · 12-bit encoder · TTL bus',
      confidence: 'XL330 family confirmed · M288-T likely / seen on press prototype',
    };
  }
  if (name.includes('np_f')) {
    return {
      name: 'NP-F550 POWER PACK',
      eyebrow: 'REMOVABLE BATTERY / 2,600 mAh',
      detail: 'Approx. one hour runtime, depending on use',
      confidence: 'Current product fact · CAD volume is a legacy F970 proxy',
    };
  }
  if (name.includes('raspberry_pi')) {
    return {
      name: 'RADXA ZERO 3W ENVELOPE',
      eyebrow: 'COMPUTE / RK3566 + AI ACCELERATOR',
      detail: '1 GB RAM · 32 GB storage · 65 × 30 mm board',
      confidence: 'Current compute fact · CAD uses a legacy Pi Zero proxy',
    };
  }
  if (name.includes('robot_hat') || name.includes('pcb')) {
    return {
      name: 'ROBOT HAT + I/O',
      eyebrow: 'AUDIO / SENSOR / BUS INTERFACE',
      detail: 'Microphone path, speaker output and peripheral links',
      confidence: 'Function confirmed · exact production layout conceptual',
    };
  }
  if (name.includes('lens') || name.includes('face') || name.includes('noenoeil')) {
    return {
      name: 'VISION + 8×8 TOF',
      eyebrow: 'CAMERA / DEPTH MATRIX',
      detail: 'Head-mounted sensing follows the duck’s gaze',
      confidence: 'Functions confirmed · final camera spec and placement not final',
    };
  }
  if (name.includes('speaker')) {
    return {
      name: 'VOICE SYSTEM',
      eyebrow: 'SPEAKER / GENERATED PER-ROBOT VOICE',
      detail: 'Microduck quacks in a voice that is its own',
      confidence: 'Function confirmed · placement from simulator geometry',
    };
  }
  const cleanName = meshName.replace(/\.stl$/i, '').replaceAll('_', ' ').toUpperCase();
  return {
    name: cleanName,
    eyebrow: `${category.toUpperCase()} / SIMULATOR ASSEMBLY`,
    detail: 'Animated inside the official kinematic body hierarchy',
    confidence: category === 'shell' ? 'Official simulator geometry' : 'Concept engineering view',
  };
}

function explodeVector(meshName: string, bodyName: string, index: number) {
  const name = meshName.toLowerCase();
  if (name.includes('left_shell')) return new THREE.Vector3(0, 0.12, 0);
  if (name.includes('right_shell')) return new THREE.Vector3(0, -0.12, 0);
  if (name.includes('top_head')) return new THREE.Vector3(0, 0.02, 0.12);
  if (name.includes('bottom_head')) return new THREE.Vector3(0, -0.01, -0.1);
  if (name.includes('jaw') || name.includes('mouth')) return new THREE.Vector3(0.12, 0, -0.035);
  if (name.includes('lens') || name.includes('face') || name.includes('noenoeil')) {
    return new THREE.Vector3(0.11, 0, ((index % 4) - 1.5) * 0.038);
  }
  if (name.includes('np_f')) return new THREE.Vector3(-0.13, 0, 0.01);
  if (name.includes('pcb')) {
    return new THREE.Vector3(0.09, 0, name.includes('robot_hat') ? -0.075 : 0.075);
  }
  if (bodyName.includes('left') || bodyName === 'yaw2roll' || bodyName === 'hip_l') {
    return new THREE.Vector3(0, 0.09, 0);
  }
  if (bodyName.includes('right') || bodyName === 'bearing_roll' || bodyName === 'hip_l_2') {
    return new THREE.Vector3(0, -0.09, 0);
  }
  if (bodyName.includes('neck') || bodyName.includes('jaw')) return new THREE.Vector3(0, 0, 0.09);
  return new THREE.Vector3((index % 3) * 0.018 - 0.018, 0, 0.045 + (index % 4) * 0.008);
}

const ASSEMBLY_DURATION = 0.96;
const DETAIL_GAIT_AMPLITUDE = 0.3;
const MODEL_BASE_YAW = -0.08;
const STAGE_ROTATION_STEP = Math.PI / 2;
const STAGE_ROTATION_DURATION = 0.92;
const BEAK_CYCLE_SECONDS = 1.35;
const BEAK_OPEN_ANGLE = THREE.MathUtils.degToRad(14);
const BEAK_PIVOT_LOCAL = new THREE.Vector3(0, 0.008, 0.004);

const ASSEMBLY_DELAY: Record<PartCategory, number> = {
  structure: 0,
  compute: 0.08,
  power: 0.11,
  motor: 0.18,
  sensor: 0.28,
  shell: 0.38,
};

function assemblyVector(vector: THREE.Vector3, index: number, internal: boolean) {
  const angle = index * 2.399963229728653;
  const radius = internal ? 0.19 : 0.25;
  return vector
    .clone()
    .multiplyScalar(internal ? 1.75 : 2.1)
    .add(
      new THREE.Vector3(
        Math.cos(angle) * radius,
        ((index % 5) - 2) * 0.046,
        Math.sin(angle) * radius,
      ),
    );
}

function assemblyArc(index: number, internal: boolean) {
  const angle = index * 2.399963229728653 + Math.PI / 2;
  const radius = internal ? 0.038 : 0.052;
  return new THREE.Vector3(
    Math.cos(angle) * radius,
    ((index % 3) - 1) * 0.018,
    Math.sin(angle) * radius,
  );
}

function assemblyEase(t: number) {
  const overshoot = 1.38;
  const shifted = t - 1;
  return 1 + (overshoot + 1) * shifted * shifted * shifted + overshoot * shifted * shifted;
}

function isLowerBeak(meshName: string) {
  const name = meshName.toLowerCase();
  return name === 'jaw.stl' || name === 'jaw_soft.stl' || name === 'bottom_head_shell.stl';
}

const MICRODUCK_GAIT_CENTER = (() => {
  const center = new Float32Array(MICRODUCK_WALK_CHANNELS);
  for (const pose of MICRODUCK_WALK_FRAMES) {
    for (let channel = 0; channel < MICRODUCK_WALK_CHANNELS; channel += 1) {
      center[channel] += pose[channel];
    }
  }
  for (let channel = 0; channel < MICRODUCK_WALK_CHANNELS; channel += 1) {
    center[channel] /= MICRODUCK_WALK_FRAMES.length;
  }
  return center;
})();

function applyJointAngle(joint: JointRig, angle: number) {
  joint.currentAngle = THREE.MathUtils.clamp(angle, joint.min, joint.max);
  joint.body.quaternion.copy(joint.baseQuaternion);
  joint.body.quaternion.multiply(
    new THREE.Quaternion().setFromAxisAngle(joint.axis, joint.currentAngle),
  );
}

function setJoint(joints: Map<string, JointRig>, name: string, angle: number) {
  const joint = joints.get(name);
  if (!joint) return;
  joint.gaitAngle = angle;
  applyJointAngle(joint, angle + joint.ikOffset);
}

function catmullRom(previous: number, start: number, end: number, next: number, t: number) {
  const t2 = t * t;
  const t3 = t2 * t;
  return 0.5 * (
    2 * start +
    (-previous + end) * t +
    (2 * previous - 5 * start + 4 * end - next) * t2 +
    (-previous + 3 * start - 3 * end + next) * t3
  );
}

function samplePolicyGait(phase: number, output: Float32Array) {
  const frameCount = MICRODUCK_WALK_FRAMES.length;
  const framePosition = (((phase % 1) + 1) % 1) * frameCount;
  const frameStart = Math.floor(framePosition);
  const t = framePosition - frameStart;
  const previous = MICRODUCK_WALK_FRAMES[(frameStart - 1 + frameCount) % frameCount];
  const start = MICRODUCK_WALK_FRAMES[frameStart % frameCount];
  const end = MICRODUCK_WALK_FRAMES[(frameStart + 1) % frameCount];
  const next = MICRODUCK_WALK_FRAMES[(frameStart + 2) % frameCount];

  for (let channel = 0; channel < MICRODUCK_WALK_CHANNELS; channel += 1) {
    output[channel] = catmullRom(
      previous[channel],
      start[channel],
      end[channel],
      next[channel],
      t,
    );
  }
}

export function MicroduckBlueprint() {
  const shellRef = useRef<HTMLElement>(null);
  const hostRef = useRef<HTMLDivElement>(null);
  const stepRefs = useRef<Array<HTMLElement | null>>([]);
  const sceneApi = useRef<SceneApi | null>(null);
  const navigateToStepRef = useRef<((index: number) => void) | null>(null);
  const activeStepRef = useRef(0);
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [activeStep, setActiveStep] = useState(0);
  const [inspection, setInspection] = useState<Inspection | null>(null);
  const [telemetry, setTelemetry] = useState<Telemetry>({ phase: 0, hip: 0, tilt: 0 });

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;

    let disposed = false;
    let frame = 0;
    let explosion = 0;
    let explosionTarget = 0;
    let currentLayer: LayerPreset = 'ALL';
    let currentStageIndex = 0;
    let hoveredPart: Explodable | null = null;
    let lastInspectionUpdate = 0;
    let lastTelemetryUpdate = 0;
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let assemblyStartTime: number | null = null;
    let assemblyComplete = reducedMotion;
    let cameraAnimationStart = 0;
    let cameraAnimationDuration = 0.92;
    const initialStage = LAYERS[0];
    const initialTarget = new THREE.Vector3(...initialStage.target);
    const initialCameraPosition = initialTarget.clone().add(
      new THREE.Vector3(...initialStage.cameraOffset),
    );
    const cameraFrom = new THREE.Vector3();
    const targetFrom = new THREE.Vector3();
    const cameraGoal = initialCameraPosition.clone();
    const targetGoal = initialTarget.clone();
    let zoomFrom = initialStage.zoom;
    let zoomGoal = initialStage.zoom;
    let cameraAnimating = false;
    let modelRotationFrom = MODEL_BASE_YAW;
    let modelRotationGoal = MODEL_BASE_YAW;
    let modelRotationStart = 0;
    let modelRotating = false;
    const stageRotationAxis = new THREE.Vector3(0, 1, 0);

    const scene = new THREE.Scene();
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0xf4f1e8, 0);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.domElement.className = 'blueprint-canvas';
    renderer.domElement.setAttribute(
      'aria-label',
      'Interactive 3D Microduck; drag empty space to orbit, drag a leg or the head to pose it, or swipe vertically between sections',
    );
    renderer.domElement.setAttribute('role', 'img');
    host.appendChild(renderer.domElement);

    const camera = new THREE.OrthographicCamera(-0.2, 0.2, 0.2, -0.2, 0.001, 10);
    camera.position.copy(initialCameraPosition);
    camera.zoom = initialStage.zoom;
    camera.updateProjectionMatrix();

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.copy(initialTarget);
    controls.enableDamping = true;
    controls.dampingFactor = 0.075;
    controls.enableZoom = false;
    controls.enablePan = false;
    controls.enableRotate = true;
    controls.minPolarAngle = Math.PI * 0.16;
    controls.maxPolarAngle = Math.PI * 0.84;
    controls.touches.ONE = THREE.TOUCH.PAN;
    controls.touches.TWO = THREE.TOUCH.DOLLY_PAN;
    renderer.domElement.style.touchAction = 'none';
    controls.addEventListener('start', () => {
      cameraAnimating = false;
    });

    const modelAnchor = new THREE.Group();
    modelAnchor.rotation.y = MODEL_BASE_YAW;
    scene.add(modelAnchor);

    const root = new THREE.Group();
    root.rotation.x = -Math.PI / 2;
    modelAnchor.add(root);

    const gridFine = new THREE.GridHelper(1.8, 72, 0xb7b2aa, 0xd1cdc5);
    (gridFine.material as THREE.Material).transparent = true;
    (gridFine.material as THREE.Material).opacity = 0.16;
    (gridFine.material as THREE.Material).blending = THREE.NormalBlending;
    (gridFine.material as THREE.Material).depthWrite = false;
    scene.add(gridFine);

    const gridMajor = new THREE.GridHelper(1.8, 18, 0x8c8881, 0xaaa59d);
    (gridMajor.material as THREE.Material).transparent = true;
    (gridMajor.material as THREE.Material).opacity = 0.22;
    (gridMajor.material as THREE.Material).blending = THREE.NormalBlending;
    (gridMajor.material as THREE.Material).depthWrite = false;
    gridMajor.position.y = 0.0002;
    scene.add(gridMajor);

    const joints = new Map<string, JointRig>();
    const jointByBody = new Map<THREE.Group, JointRig>();
    const bodies = new Map<string, THREE.Group>();
    const parts: Explodable[] = [];
    const partByMesh = new Map<THREE.Object3D, Explodable>();
    const beakParts: BeakPart[] = [];
    const edgeCache = new Map<string, THREE.EdgesGeometry>();
    let ikInteraction: IKInteraction | null = null;
    let ikRootWeight = 0;
    let trunkBody: THREE.Group | null = null;
    const trunkBasePosition = new THREE.Vector3(0, 0, 0.12);
    const trunkBaseQuaternion = new THREE.Quaternion();
    const ikRootPosition = trunkBasePosition.clone();
    const ikRootQuaternion = trunkBaseQuaternion.clone();

    const resize = () => {
      const width = Math.max(host.clientWidth, 1);
      const height = Math.max(host.clientHeight, 1);
      renderer.setSize(width, height, false);
      const aspect = width / height;
      const frustum = width < 720 ? 0.46 : 0.36;
      camera.left = (-frustum * aspect) / 2;
      camera.right = (frustum * aspect) / 2;
      camera.top = frustum / 2;
      camera.bottom = -frustum / 2;
      zoomGoal = LAYERS[currentStageIndex].zoom * (width < 720 ? 1.2 : 1);
      if (!cameraAnimating) camera.zoom = zoomGoal;
      camera.updateProjectionMatrix();
    };

    const resizeObserver = new ResizeObserver(resize);
    resizeObserver.observe(host);
    resize();

    const raycaster = new THREE.Raycaster();
    const pointer = new THREE.Vector2();
    const restoreHovered = () => {
      if (!hoveredPart) return;
      hoveredPart.mesh.material.uniforms.uColor.value.copy(hoveredPart.baseColor);
      hoveredPart.outline.color.set(hoveredPart.category === 'motor' ? 0xa82768 : 0x65676b);
      hoveredPart = null;
    };

    const inspectAtPointer = (event: PointerEvent) => {
      if (!parts.length || !assemblyComplete || event.pointerType === 'touch') return;
      const rect = renderer.domElement.getBoundingClientRect();
      pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(pointer, camera);
      const hit = raycaster.intersectObjects(
        parts
          .filter((part) => currentLayer === 'ALL' || layerMatches(currentLayer, part.category))
          .map((part) => part.mesh),
        false,
      )[0];
      const next = hit
        ? parts.find((part) => part.mesh === hit.object) ?? null
        : null;

      if (!ikInteraction) {
        const draggable = next && ikChainForPart(next) &&
          (currentLayer === 'ALL' || (currentLayer === 'MOTORS' && next.category === 'motor'));
        renderer.domElement.style.cursor = draggable ? 'move' : 'grab';
      }

      if (next !== hoveredPart) {
        restoreHovered();
        hoveredPart = next;
        if (hoveredPart) {
          hoveredPart.mesh.material.uniforms.uColor.value.set(0xe8407f);
          hoveredPart.outline.color.set(0xa82768);
        }
      }

      const now = performance.now();
      if (!hoveredPart) {
        setInspection(null);
      } else if (now - lastInspectionUpdate > 40) {
        lastInspectionUpdate = now;
        const copy = inspectionCopy(hoveredPart.mesh.name, hoveredPart.category);
        setInspection({
          ...copy,
          x: Math.min(event.clientX, window.innerWidth - 252),
          y: Math.min(event.clientY, window.innerHeight - 168),
        });
      }
    };

    const clearInspection = () => {
      restoreHovered();
      setInspection(null);
      if (!ikInteraction) renderer.domElement.style.cursor = 'grab';
    };

    const setRayFromPointer = (event: PointerEvent) => {
      const rect = renderer.domElement.getBoundingClientRect();
      pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
      pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
      raycaster.setFromCamera(pointer, camera);
    };

    const collectIKJoints = (body: THREE.Group, chain: IKChainSpec) => {
      const result: JointRig[] = [];
      let cursor: THREE.Object3D | null = body;
      while (cursor && cursor !== root && cursor !== trunkBody) {
        if (cursor instanceof THREE.Group && chain.bodies.includes(cursor.name)) {
          const joint = jointByBody.get(cursor);
          if (joint) result.push(joint);
        }
        cursor = cursor.parent;
      }
      return result;
    };

    const pickIKHit = (event: PointerEvent): IKHit | null => {
      if (!assemblyComplete || (currentLayer !== 'ALL' && currentLayer !== 'MOTORS')) {
        return null;
      }
      setRayFromPointer(event);
      const candidates = parts.filter((part) => {
        if (currentLayer === 'MOTORS' && part.category !== 'motor') return false;
        return part.mesh.material.uniforms.uOpacity.value > 0.055 || part.outline.opacity > 0.12;
      });
      const hit = raycaster.intersectObjects(candidates.map((part) => part.mesh), false)[0];
      if (!hit) return null;
      const part = partByMesh.get(hit.object);
      if (!part) return null;
      const chain = ikChainForPart(part);
      const bodyName = part.mesh.userData.bodyName as string | undefined;
      const body = bodyName ? bodies.get(bodyName) : null;
      if (!chain || !body) return null;
      const ikJoints = collectIKJoints(body, chain);
      if (!ikJoints.length) return null;
      return {
        part,
        chain,
        joints: ikJoints,
        effector: part.mesh,
        effectorLocal: part.mesh.worldToLocal(hit.point.clone()),
        point: hit.point.clone(),
      };
    };

    const beginIK = (event: PointerEvent, hit: IKHit) => {
      const planeNormal = camera.getWorldDirection(new THREE.Vector3()).normalize();
      ikInteraction = {
        pointerId: event.pointerId,
        part: hit.part,
        chain: hit.chain,
        joints: hit.joints,
        effector: hit.effector,
        effectorLocal: hit.effectorLocal,
        plane: new THREE.Plane().setFromNormalAndCoplanarPoint(planeNormal, hit.point),
        target: hit.point.clone(),
      };
      ikRootWeight = 1;
      if (trunkBody) {
        ikRootPosition.copy(trunkBody.position);
        ikRootQuaternion.copy(trunkBody.quaternion);
      }
      cameraAnimating = false;
      modelRotating = false;
      controls.enabled = false;
      clearInspection();
      hoveredPart = hit.part;
      hoveredPart.mesh.material.uniforms.uColor.value.set(0xe8407f);
      hoveredPart.outline.color.set(0xa82768);
      renderer.domElement.style.cursor = 'grabbing';
      renderer.domElement.setPointerCapture?.(event.pointerId);
    };

    const updateIKTarget = (event: PointerEvent) => {
      const interaction = ikInteraction;
      if (!interaction || interaction.pointerId !== event.pointerId) return;
      setRayFromPointer(event);
      const point = raycaster.ray.intersectPlane(interaction.plane, new THREE.Vector3());
      if (point) interaction.target.copy(point);
    };

    const finishIK = (releaseCapture = true) => {
      const interaction = ikInteraction;
      if (!interaction) return;
      ikInteraction = null;
      controls.enabled = true;
      if (
        releaseCapture &&
        renderer.domElement.hasPointerCapture?.(interaction.pointerId)
      ) {
        renderer.domElement.releasePointerCapture(interaction.pointerId);
      }
      restoreHovered();
      renderer.domElement.style.cursor = 'grab';
    };

    const onDirectPointerDown = (event: PointerEvent) => {
      if (event.pointerType === 'touch' || ikInteraction) return;
      const hit = pickIKHit(event);
      if (!hit) return;
      beginIK(event, hit);
      event.preventDefault();
      event.stopImmediatePropagation();
    };

    const onDirectPointerMove = (event: PointerEvent) => {
      if (event.pointerType === 'touch' || ikInteraction?.pointerId !== event.pointerId) return;
      updateIKTarget(event);
      event.preventDefault();
      event.stopImmediatePropagation();
    };

    const onDirectPointerEnd = (event: PointerEvent) => {
      if (event.pointerType === 'touch' || ikInteraction?.pointerId !== event.pointerId) return;
      finishIK();
      event.preventDefault();
      event.stopImmediatePropagation();
    };

    let cancelTouchGestureState = () => {};

    const onLostPointerCapture = (event: PointerEvent) => {
      if (ikInteraction?.pointerId === event.pointerId) {
        finishIK(false);
        cancelTouchGestureState();
      }
    };

    const onWindowBlur = () => {
      finishIK();
      cancelTouchGestureState();
    };
    const onIKKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        finishIK();
        cancelTouchGestureState();
      }
    };

    renderer.domElement.addEventListener('pointerdown', onDirectPointerDown, true);
    renderer.domElement.addEventListener('pointermove', onDirectPointerMove, true);
    renderer.domElement.addEventListener('pointerup', onDirectPointerEnd, true);
    renderer.domElement.addEventListener('pointercancel', onDirectPointerEnd, true);
    renderer.domElement.addEventListener('lostpointercapture', onLostPointerCapture);
    window.addEventListener('blur', onWindowBlur);
    window.addEventListener('keydown', onIKKeyDown);

    const touchPointers = new Set<number>();
    const touchStart = new THREE.Vector2();
    const touchPrevious = new THREE.Vector2();
    let touchPointerId: number | null = null;
    let touchIKCandidate: IKHit | null = null;
    let touchGesture: 'idle' | 'pending' | 'orbit' | 'navigate' | 'ik' | 'blocked' = 'idle';

    const resetTouchGesture = () => {
      touchPointerId = null;
      touchIKCandidate = null;
      touchGesture = touchPointers.size ? 'blocked' : 'idle';
    };

    cancelTouchGestureState = () => {
      touchPointers.clear();
      touchPointerId = null;
      touchIKCandidate = null;
      touchGesture = 'idle';
    };

    const beginTouchGesture = (event: PointerEvent) => {
      if (event.pointerType !== 'touch') return;
      touchPointers.add(event.pointerId);
      renderer.domElement.setPointerCapture?.(event.pointerId);

      if (touchPointers.size !== 1) {
        if (ikInteraction) finishIK();
        touchGesture = 'blocked';
        touchPointerId = null;
        touchIKCandidate = null;
        return;
      }

      touchPointerId = event.pointerId;
      touchStart.set(event.clientX, event.clientY);
      touchPrevious.copy(touchStart);
      touchIKCandidate = pickIKHit(event);
      touchGesture = 'pending';
    };

    const moveTouchGesture = (event: PointerEvent) => {
      if (
        event.pointerType !== 'touch' ||
        event.pointerId !== touchPointerId ||
        touchPointers.size !== 1 ||
        touchGesture === 'blocked'
      ) return;

      const totalX = event.clientX - touchStart.x;
      const totalY = event.clientY - touchStart.y;
      const absX = Math.abs(totalX);
      const absY = Math.abs(totalY);

      if (touchGesture === 'pending') {
        if (Math.max(absX, absY) < 10) return;
        if (absY > absX * 1.15) {
          touchGesture = 'navigate';
        } else if (absX > absY * 1.15) {
          if (touchIKCandidate) {
            touchGesture = 'ik';
            beginIK(event, touchIKCandidate);
          } else {
            touchGesture = assemblyComplete ? 'orbit' : 'blocked';
            if (touchGesture === 'orbit') {
              cameraAnimating = false;
              modelRotating = false;
            }
          }
        } else if (Math.max(absX, absY) < 24) {
          return;
        } else if (absX > absY && touchIKCandidate) {
          touchGesture = 'ik';
          beginIK(event, touchIKCandidate);
        } else {
          touchGesture = absX > absY && assemblyComplete ? 'orbit' : 'navigate';
          if (touchGesture === 'orbit') {
            cameraAnimating = false;
            modelRotating = false;
          }
        }
      }

      if (touchGesture === 'ik') {
        event.preventDefault();
        updateIKTarget(event);
      } else if (touchGesture === 'orbit') {
        event.preventDefault();
        const deltaX = event.clientX - touchPrevious.x;
        const deltaY = event.clientY - touchPrevious.y;
        const rotationScale = (Math.PI * 1.35) / Math.max(host.clientHeight, 1);
        controls.rotateLeft(deltaX * rotationScale);
        controls.rotateUp(deltaY * rotationScale * 0.72);
      }

      touchPrevious.set(event.clientX, event.clientY);
    };

    const endTouchGesture = (event: PointerEvent, cancelled = false) => {
      if (event.pointerType !== 'touch') return;

      const isPrimaryGesture = event.pointerId === touchPointerId;
      const gesture = touchGesture;
      const verticalTravel = event.clientY - touchStart.y;
      touchPointers.delete(event.pointerId);

      if (isPrimaryGesture && gesture === 'ik' && ikInteraction) {
        finishIK();
      } else if (
        !cancelled &&
        isPrimaryGesture &&
        gesture === 'navigate' &&
        Math.abs(verticalTravel) >= 48
      ) {
        const direction = verticalTravel < 0 ? 1 : -1;
        navigateToStepRef.current?.(activeStepRef.current + direction);
      }

      if (renderer.domElement.hasPointerCapture?.(event.pointerId)) {
        renderer.domElement.releasePointerCapture(event.pointerId);
      }
      resetTouchGesture();
    };

    const cancelTouchGesture = (event: PointerEvent) => endTouchGesture(event, true);
    renderer.domElement.addEventListener('pointerdown', beginTouchGesture);
    renderer.domElement.addEventListener('pointermove', moveTouchGesture);
    renderer.domElement.addEventListener('pointerup', endTouchGesture);
    renderer.domElement.addEventListener('pointercancel', cancelTouchGesture);

    const focusStage = (stageIndex: number) => {
      finishIK();
      cancelTouchGestureState();
      currentStageIndex = THREE.MathUtils.clamp(Math.round(stageIndex), 0, LAYERS.length - 1);
      const stage = LAYERS[currentStageIndex];
      const stageRotation = currentStageIndex * STAGE_ROTATION_STEP;
      currentLayer = stage.id;
      explosionTarget = stage.explosion;
      clearInspection();

      cameraFrom.copy(camera.position);
      targetFrom.copy(controls.target);
      zoomFrom = camera.zoom;
      targetGoal.set(...stage.target).applyAxisAngle(stageRotationAxis, stageRotation);
      cameraGoal.copy(targetGoal).add(new THREE.Vector3(...stage.cameraOffset));
      zoomGoal = stage.zoom * (host.clientWidth < 720 ? 1.2 : 1);
      cameraAnimationStart = performance.now() / 1000;
      cameraAnimationDuration = reducedMotion ? 0 : 0.92;
      modelRotationFrom = modelAnchor.rotation.y;
      modelRotationGoal = MODEL_BASE_YAW + stageRotation;
      modelRotationStart = cameraAnimationStart;

      if (reducedMotion) {
        modelAnchor.rotation.y = modelRotationGoal;
        camera.position.copy(cameraGoal);
        controls.target.copy(targetGoal);
        camera.zoom = zoomGoal;
        camera.updateProjectionMatrix();
        cameraAnimating = false;
        modelRotating = false;
      } else {
        cameraAnimating = true;
        modelRotating = true;
      }
    };

    sceneApi.current = { focusStage };

    renderer.domElement.addEventListener('pointermove', inspectAtPointer);
    renderer.domElement.addEventListener('pointerleave', clearInspection);

    const loader = new GLTFLoader();
    Promise.all([
      fetch('/robot/mjlab/kinematics.json').then(async (response) => {
        if (!response.ok) throw new Error(`Kinematics failed: ${response.status}`);
        return (await response.json()) as Kinematics;
      }),
      loader.loadAsync('/robot/mjlab/microduck.glb'),
    ])
      .then(([kinematics, gltf]) => {
        if (disposed) return;
        const geometryByName = new Map<string, THREE.BufferGeometry>();
        gltf.scene.traverse((object) => {
          const candidate = object as THREE.Mesh;
          if (!candidate.isMesh || !candidate.geometry) return;
          const meshName =
            (candidate.userData.meshFile as string | undefined) ||
            candidate.name ||
            candidate.geometry.name;
          if (meshName && !geometryByName.has(meshName)) {
            geometryByName.set(meshName, candidate.geometry as THREE.BufferGeometry);
          }
        });

        for (const body of kinematics.bodies) {
          const group = new THREE.Group();
          group.name = body.name;
          group.position.set(...body.pos);
          group.quaternion.copy(quaternionFromMjcf(body.quat));
          bodies.set(body.name, group);
        }

        for (const body of kinematics.bodies) {
          const group = bodies.get(body.name);
          if (!group) continue;
          const parent = body.parent ? bodies.get(body.parent) : null;
          (parent ?? root).add(group);
          if (body.joint && (!body.joint.type || body.joint.type === 'hinge')) {
            const joint: JointRig = {
              name: body.joint.name,
              body: group,
              baseQuaternion: group.quaternion.clone(),
              axis: new THREE.Vector3(...body.joint.axis).normalize(),
              min: body.joint.range?.[0] ?? -Math.PI,
              max: body.joint.range?.[1] ?? Math.PI,
              gaitAngle: 0,
              ikOffset: 0,
              currentAngle: 0,
            };
            joints.set(body.joint.name, joint);
            jointByBody.set(group, joint);
          }
        }

        trunkBody = bodies.get('trunk_base') ?? null;
        if (trunkBody) {
          trunkBasePosition.copy(trunkBody.position);
          trunkBaseQuaternion.copy(trunkBody.quaternion);
        }

        let partIndex = 0;
        for (const body of kinematics.bodies) {
          const group = bodies.get(body.name);
          if (!group) continue;
          const duplicates = new Set<string>();
          for (const geom of body.geoms) {
            if (!geom.mesh) continue;
            const duplicateKey = `${geom.mesh}|${geom.pos?.join(',')}|${geom.quat?.join(',')}`;
            if (duplicates.has(duplicateKey)) continue;
            duplicates.add(duplicateKey);
            const geometry = geometryByName.get(geom.mesh);
            if (!geometry) continue;

            const internal = isInternal(geom.mesh);
            const category = categoryFor(geom.mesh);
            const baseColor = new THREE.Color(CATEGORY_COLORS[category]);
            const material = new THREE.ShaderMaterial({
              vertexShader,
              fragmentShader,
              uniforms: {
                uColor: { value: baseColor.clone() },
                uInk: { value: new THREE.Color(0x77797c) },
                uOpacity: { value: reducedMotion ? (internal ? 0.19 : 0.11) : 0 },
              },
              transparent: true,
              depthWrite: false,
              depthTest: true,
              blending: THREE.NormalBlending,
              toneMapped: false,
              side: THREE.DoubleSide,
            });
            const mesh = new THREE.Mesh(geometry, material);
            mesh.name = geom.mesh;
            mesh.userData.bodyName = body.name;
            if (geom.pos) mesh.position.set(...geom.pos);
            if (geom.quat) mesh.quaternion.copy(quaternionFromMjcf(geom.quat));
            group.add(mesh);

            let edgeGeometry = edgeCache.get(geom.mesh);
            if (!edgeGeometry) {
              edgeGeometry = new THREE.EdgesGeometry(geometry, 34);
              edgeCache.set(geom.mesh, edgeGeometry);
            }
            const outlineMaterial = new THREE.LineBasicMaterial({
              color: internal ? 0x77797c : 0x65676b,
              transparent: true,
              opacity: reducedMotion ? (internal ? 0.5 : 0.46) : 0,
              depthWrite: false,
              blending: THREE.NormalBlending,
              toneMapped: false,
            });
            const outline = new THREE.LineSegments(edgeGeometry, outlineMaterial);
            outline.renderOrder = 3;
            mesh.add(outline);

            const basePosition = mesh.position.clone();
            const partExplosionVector = explodeVector(geom.mesh, body.name, partIndex);
            const partAssemblyVector = assemblyVector(partExplosionVector, partIndex, internal);
            const partAssemblyArc = assemblyArc(partIndex, internal);
            const baseQuaternion = mesh.quaternion.clone();
            if (!reducedMotion) {
              mesh.position.copy(basePosition).add(partAssemblyVector);
            }
            const part: Explodable = {
              mesh,
              outline: outlineMaterial,
              base: basePosition,
              baseColor,
              vector: partExplosionVector,
              assemblyVector: partAssemblyVector,
              assemblyArc: partAssemblyArc,
              assemblyDelay: ASSEMBLY_DELAY[category] + (partIndex % 6) * 0.032,
              shell: !internal,
              category,
            };
            parts.push(part);
            partByMesh.set(mesh, part);
            if (isLowerBeak(geom.mesh)) {
              beakParts.push({
                mesh,
                basePosition,
                baseQuaternion,
                pivot: BEAK_PIVOT_LOCAL.clone().applyQuaternion(baseQuaternion).add(basePosition),
                axis: new THREE.Vector3(1, 0, 0).applyQuaternion(baseQuaternion).normalize(),
              });
            }
            partIndex += 1;
          }
        }
        if (!reducedMotion) assemblyStartTime = performance.now() / 1000 + 0.14;
        setStatus('ready');
      })
      .catch((error) => {
        console.error(error);
        if (!disposed) setStatus('error');
      });

    let previousFrameTime = performance.now() / 1000;
    let motionTime = 0;
    let beakTime = 0;
    let motionRate = reducedMotion ? 0 : 1;
    let gaitAmplitude = 1;
    const focusTeal = new THREE.Color(0x0bbac6);
    const focusAmber = new THREE.Color(0xdf7a32);
    const focusInk = new THREE.Color(0x45484c);
    const defaultInk = new THREE.Color(0x65676b);
    const assemblyFlash = new THREE.Color(0xe8c92a);
    const gaitSample = new Float32Array(MICRODUCK_WALK_CHANNELS);
    const trunkTilt = new THREE.Quaternion();
    const trunkEuler = new THREE.Euler(0, 0, 0, 'ZYX');
    const trunkGaitPosition = new THREE.Vector3();
    const trunkGaitQuaternion = new THREE.Quaternion();
    const beakPivot = new THREE.Vector3();
    const beakOffset = new THREE.Vector3();
    const beakRotation = new THREE.Quaternion();
    const ikPivot = new THREE.Vector3();
    const ikEffector = new THREE.Vector3();
    const ikAxis = new THREE.Vector3();
    const ikFrom = new THREE.Vector3();
    const ikTo = new THREE.Vector3();
    const ikCross = new THREE.Vector3();

    const solveActiveIK = () => {
      const interaction = ikInteraction;
      if (!interaction) return;
      const tolerance = interaction.chain.id === 'head' ? 0.002 : 0.0012;

      for (let iteration = 0; iteration < 10; iteration += 1) {
        ikEffector.copy(interaction.effectorLocal);
        interaction.effector.localToWorld(ikEffector);
        if (ikEffector.distanceTo(interaction.target) <= tolerance) break;

        for (const joint of interaction.joints) {
          joint.body.getWorldPosition(ikPivot);
          ikAxis.copy(joint.axis).transformDirection(joint.body.matrixWorld);
          ikEffector.copy(interaction.effectorLocal);
          interaction.effector.localToWorld(ikEffector);
          ikFrom.subVectors(ikEffector, ikPivot);
          ikTo.subVectors(interaction.target, ikPivot);
          ikFrom.addScaledVector(ikAxis, -ikFrom.dot(ikAxis));
          ikTo.addScaledVector(ikAxis, -ikTo.dot(ikAxis));
          if (ikFrom.lengthSq() < 1e-10 || ikTo.lengthSq() < 1e-10) continue;
          ikFrom.normalize();
          ikTo.normalize();
          ikCross.crossVectors(ikFrom, ikTo);
          const signedDelta = Math.atan2(
            ikAxis.dot(ikCross),
            THREE.MathUtils.clamp(ikFrom.dot(ikTo), -1, 1),
          );
          const delta = THREE.MathUtils.clamp(signedDelta * 0.68, -0.14, 0.14);
          applyJointAngle(joint, joint.currentAngle + delta);
          joint.ikOffset = joint.currentAngle - joint.gaitAngle;
          modelAnchor.updateMatrixWorld(true);
        }
      }
    };

    const animate = () => {
      if (disposed) return;
      frame = requestAnimationFrame(animate);
      const frameTime = performance.now() / 1000;
      const delta = Math.min(Math.max(frameTime - previousFrameTime, 0), 0.05);
      previousFrameTime = frameTime;
      motionRate = THREE.MathUtils.damp(
        motionRate,
        reducedMotion ? 0 : 1,
        12,
        delta || 0.016,
      );
      motionTime += delta * motionRate;

      explosion = THREE.MathUtils.damp(explosion, explosionTarget, 2.8, delta || 0.016);
      const easedExplosion = explosion * explosion * (3 - 2 * explosion);
      let assemblyInProgress = false;
      for (let index = 0; index < parts.length; index += 1) {
        const part = parts[index];
        const stagger = (index % 7) * 0.018;
        const localExplosion = THREE.MathUtils.smoothstep(easedExplosion, stagger, 1);
        let assemblyOffset = 0;
        let assemblyArcAmount = 0;
        let assemblyReveal = 1;
        let arrivalPulse = 0;
        if (!assemblyComplete && assemblyStartTime !== null) {
          const assemblyProgress = THREE.MathUtils.clamp(
            (frameTime - assemblyStartTime - part.assemblyDelay) / ASSEMBLY_DURATION,
            0,
            1,
          );
          assemblyInProgress ||= assemblyProgress < 1;
          assemblyOffset = 1 - assemblyEase(assemblyProgress);
          assemblyArcAmount = Math.sin(Math.PI * assemblyProgress) * (1 - assemblyProgress);
          assemblyReveal = THREE.MathUtils.smoothstep(assemblyProgress, 0.025, 0.2);
          const pulseWindow = Math.max(0, 1 - Math.abs(assemblyProgress - 0.84) / 0.15);
          arrivalPulse = pulseWindow * pulseWindow;
        }
        const keepServoMounted = currentLayer === 'MOTORS' && part.category === 'motor';
        const positionExplosion = keepServoMounted ? 0 : localExplosion;
        part.mesh.position
          .copy(part.base)
          .addScaledVector(part.vector, positionExplosion)
          .addScaledVector(part.assemblyVector, assemblyOffset)
          .addScaledVector(part.assemblyArc, assemblyArcAmount);
        const focused = layerMatches(currentLayer, part.category);
        const visibilityWeight = layerVisibilityWeight(currentLayer, part.category);
        let opacityTarget = part.shell
          ? THREE.MathUtils.lerp(0.11, 0.04, localExplosion)
          : THREE.MathUtils.lerp(0.19, 0.28, localExplosion);
        if (currentLayer !== 'ALL' && !focused) opacityTarget *= visibilityWeight;
        if (currentLayer !== 'ALL' && focused) opacityTarget = Math.max(opacityTarget, 0.34);
        part.mesh.material.uniforms.uOpacity.value = opacityTarget * assemblyReveal;
        let outlineOpacity = part.shell
          ? THREE.MathUtils.lerp(0.46, 0.24, localExplosion)
          : THREE.MathUtils.lerp(0.5, 0.62, localExplosion);
        if (currentLayer !== 'ALL' && !focused) outlineOpacity *= visibilityWeight;
        if (currentLayer !== 'ALL' && focused) outlineOpacity = Math.max(outlineOpacity, 0.76);
        part.outline.opacity = outlineOpacity * assemblyReveal;

        if (part !== hoveredPart) {
          const layerColor = focused && currentLayer !== 'ALL'
            ? part.category === 'power' || part.category === 'motor' ? focusAmber : focusTeal
            : part.baseColor;
          (part.mesh.material.uniforms.uColor.value as THREE.Color).lerp(layerColor, 0.12);
          part.outline.color.lerp(
            focused && currentLayer !== 'ALL' ? focusInk : defaultInk,
            0.12,
          );
          if (arrivalPulse > 0) {
            (part.mesh.material.uniforms.uColor.value as THREE.Color).lerp(
              assemblyFlash,
              arrivalPulse * 0.68,
            );
            part.outline.color.lerp(assemblyFlash, arrivalPulse * 0.9);
          }
        }
      }
      if (
        !assemblyComplete &&
        assemblyStartTime !== null &&
        frameTime >= assemblyStartTime &&
        !assemblyInProgress
      ) {
        assemblyComplete = true;
      }
      controls.enableRotate = assemblyComplete;

      if (assemblyComplete && !reducedMotion) beakTime += delta;
      const beakPhase = (beakTime / BEAK_CYCLE_SECONDS) % 1;
      const beakOpen = Math.sin(Math.PI * beakPhase) ** 2;
      const beakAngle = BEAK_OPEN_ANGLE * beakOpen;
      for (const beakPart of beakParts) {
        beakOffset.copy(beakPart.mesh.position).sub(beakPart.basePosition);
        beakPivot.copy(beakPart.pivot).add(beakOffset);
        beakRotation.setFromAxisAngle(beakPart.axis, beakAngle);
        beakPart.mesh.position
          .sub(beakPivot)
          .applyQuaternion(beakRotation)
          .add(beakPivot);
        beakPart.mesh.quaternion.copy(beakRotation).multiply(beakPart.baseQuaternion);
      }

      // Replay the physical qpos produced by the official walking policy rather
      // than synthesizing a leg swing. The sampled root adds the matching
      // weight transfer, height compression, and forward lean.
      const gaitPhase = (motionTime / MICRODUCK_WALK_CYCLE_SECONDS) % 1;
      samplePolicyGait(gaitPhase, gaitSample);
      const gaitAmplitudeTarget = currentStageIndex === 0 ? 1 : DETAIL_GAIT_AMPLITUDE;
      gaitAmplitude = reducedMotion
        ? gaitAmplitudeTarget
        : THREE.MathUtils.damp(gaitAmplitude, gaitAmplitudeTarget, 5, delta || 0.016);
      for (let channel = 0; channel < MICRODUCK_WALK_CHANNELS; channel += 1) {
        gaitSample[channel] = MICRODUCK_GAIT_CENTER[channel] +
          (gaitSample[channel] - MICRODUCK_GAIT_CENTER[channel]) * gaitAmplitude;
      }

      ikRootWeight = ikInteraction
        ? 1
        : reducedMotion ? 0 : THREE.MathUtils.damp(ikRootWeight, 0, 8, delta || 0.016);

      if (trunkBody) {
        trunkGaitPosition.set(
          trunkBasePosition.x,
          trunkBasePosition.y + gaitSample[MICRODUCK_TRUNK_LATERAL],
          trunkBasePosition.z + gaitSample[MICRODUCK_TRUNK_HEIGHT],
        );
        trunkEuler.set(
          gaitSample[MICRODUCK_TRUNK_ROLL],
          gaitSample[MICRODUCK_TRUNK_PITCH],
          0,
          'ZYX',
        );
        trunkTilt.setFromEuler(trunkEuler);
        trunkGaitQuaternion.copy(trunkBaseQuaternion).multiply(trunkTilt);
        trunkBody.position.copy(trunkGaitPosition).lerp(ikRootPosition, ikRootWeight);
        trunkBody.quaternion.copy(trunkGaitQuaternion).slerp(ikRootQuaternion, ikRootWeight);
      }

      for (const joint of joints.values()) {
        if (!ikInteraction?.joints.includes(joint)) {
          joint.ikOffset = reducedMotion
            ? 0
            : THREE.MathUtils.damp(joint.ikOffset, 0, 10, delta || 0.016);
        }
      }
      for (let jointIndex = 0; jointIndex < MICRODUCK_JOINT_ORDER.length; jointIndex += 1) {
        setJoint(joints, MICRODUCK_JOINT_ORDER[jointIndex], gaitSample[jointIndex]);
      }
      modelAnchor.updateMatrixWorld(true);
      solveActiveIK();

      if (motionTime - lastTelemetryUpdate > 0.18) {
        lastTelemetryUpdate = motionTime;
        setTelemetry({
          phase: Math.round(gaitPhase * 100),
          hip: Number(THREE.MathUtils.radToDeg(gaitSample[2]).toFixed(1)),
          tilt: Number(
            THREE.MathUtils.radToDeg(gaitSample[MICRODUCK_TRUNK_ROLL]).toFixed(1),
          ),
        });
      }

      if (cameraAnimating) {
        const now = performance.now() / 1000;
        const linear = THREE.MathUtils.clamp(
          (now - cameraAnimationStart) / cameraAnimationDuration,
          0,
          1,
        );
        const eased = linear < 0.5 ? 4 * linear * linear * linear : 1 - Math.pow(-2 * linear + 2, 3) / 2;
        camera.position.lerpVectors(cameraFrom, cameraGoal, eased);
        controls.target.lerpVectors(targetFrom, targetGoal, eased);
        camera.zoom = THREE.MathUtils.lerp(zoomFrom, zoomGoal, eased);
        camera.updateProjectionMatrix();
        if (linear >= 1) cameraAnimating = false;
      }

      if (modelRotating) {
        const linear = THREE.MathUtils.clamp(
          (frameTime - modelRotationStart) / STAGE_ROTATION_DURATION,
          0,
          1,
        );
        const eased = linear < 0.5
          ? 4 * linear * linear * linear
          : 1 - Math.pow(-2 * linear + 2, 3) / 2;
        modelAnchor.rotation.y = THREE.MathUtils.lerp(
          modelRotationFrom,
          modelRotationGoal,
          eased,
        );
        if (linear >= 1) modelRotating = false;
      }

      if (!ikInteraction) controls.update();
      renderer.render(scene, camera);
    };
    animate();

    return () => {
      disposed = true;
      cancelAnimationFrame(frame);
      resizeObserver.disconnect();
      finishIK();
      controls.dispose();
      renderer.domElement.removeEventListener('pointerdown', onDirectPointerDown, true);
      renderer.domElement.removeEventListener('pointermove', onDirectPointerMove, true);
      renderer.domElement.removeEventListener('pointerup', onDirectPointerEnd, true);
      renderer.domElement.removeEventListener('pointercancel', onDirectPointerEnd, true);
      renderer.domElement.removeEventListener('lostpointercapture', onLostPointerCapture);
      renderer.domElement.removeEventListener('pointerdown', beginTouchGesture);
      renderer.domElement.removeEventListener('pointermove', moveTouchGesture);
      renderer.domElement.removeEventListener('pointerup', endTouchGesture);
      renderer.domElement.removeEventListener('pointercancel', cancelTouchGesture);
      renderer.domElement.removeEventListener('pointermove', inspectAtPointer);
      renderer.domElement.removeEventListener('pointerleave', clearInspection);
      window.removeEventListener('blur', onWindowBlur);
      window.removeEventListener('keydown', onIKKeyDown);
      renderer.dispose();
      if (renderer.domElement.parentElement === host) host.removeChild(renderer.domElement);
      sceneApi.current = null;
    };
  }, []);

  useEffect(() => {
    const steps = stepRefs.current.filter((step): step is HTMLElement => Boolean(step));
    if (!steps.length) return;

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let wheelDelta = 0;
    let wheelGestureLocked = false;
    let wheelGestureQuiet = true;
    let wheelTargetIndex = activeStepRef.current;
    let navigationLockUntil = 0;
    let wheelIdleTimer: number | null = null;
    let wheelReleaseTimer: number | null = null;
    let scrollSettleTimer: number | null = null;
    let touchActive = false;

    const commitStep = (index: number) => {
      if (index === activeStepRef.current) return;
      activeStepRef.current = index;
      setActiveStep(index);
      setInspection(null);
      sceneApi.current?.focusStage(index);
    };

    const scrollToStep = (index: number) => {
      const targetIndex = THREE.MathUtils.clamp(Math.round(index), 0, steps.length - 1);
      commitStep(targetIndex);
      steps[targetIndex].scrollIntoView({
        behavior: reducedMotion ? 'auto' : 'smooth',
        block: 'start',
      });
    };

    const settleScroll = () => {
      if (scrollSettleTimer !== null) {
        window.clearTimeout(scrollSettleTimer);
        scrollSettleTimer = null;
      }
      let closestIndex = 0;
      let closestDistance = Number.POSITIVE_INFINITY;

      for (let index = 0; index < steps.length; index += 1) {
        const bounds = steps[index].getBoundingClientRect();
        const distance = Math.abs(bounds.top);
        if (distance < closestDistance) {
          closestDistance = distance;
          closestIndex = index;
        }
      }

      commitStep(closestIndex);
      if (closestDistance > 2) {
        steps[closestIndex].scrollIntoView({ behavior: 'auto', block: 'start' });
      }
    };

    const scheduleScrollSettle = () => {
      if (touchActive) return;
      if (scrollSettleTimer !== null) window.clearTimeout(scrollSettleTimer);
      scrollSettleTimer = window.setTimeout(settleScroll, 160);
    };

    const scheduleWheelRelease = () => {
      if (wheelReleaseTimer !== null) return;
      wheelReleaseTimer = window.setTimeout(releaseWheelIfReady, 80);
    };

    const releaseWheelIfReady = () => {
      wheelReleaseTimer = null;
      if (!wheelGestureLocked) return;
      const targetTop = Math.abs(steps[wheelTargetIndex].getBoundingClientRect().top);
      if (
        wheelGestureQuiet &&
        targetTop <= 2 &&
        performance.now() >= navigationLockUntil
      ) {
        wheelGestureLocked = false;
        wheelDelta = 0;
        return;
      }
      scheduleWheelRelease();
    };

    const onWheel = (event: WheelEvent) => {
      if (event.ctrlKey || Math.abs(event.deltaX) > Math.abs(event.deltaY)) return;
      if (Math.abs(event.deltaY) < 0.01) return;
      const inputDirection = event.deltaY > 0 ? 1 : -1;
      const atBoundary =
        (inputDirection < 0 && activeStepRef.current === 0) ||
        (inputDirection > 0 && activeStepRef.current === steps.length - 1);
      if (!wheelGestureLocked && atBoundary) return;
      event.preventDefault();

      if (wheelIdleTimer !== null) window.clearTimeout(wheelIdleTimer);
      wheelGestureQuiet = false;
      wheelIdleTimer = window.setTimeout(() => {
        wheelGestureQuiet = true;
        scheduleWheelRelease();
      }, 180);

      if (wheelGestureLocked) return;

      const deltaScale = event.deltaMode === 1
        ? 16
        : event.deltaMode === 2 ? window.innerHeight : 1;
      wheelDelta += event.deltaY * deltaScale;
      if (Math.abs(wheelDelta) < 48) return;

      const direction = wheelDelta > 0 ? 1 : -1;
      const targetIndex = THREE.MathUtils.clamp(
        activeStepRef.current + direction,
        0,
        steps.length - 1,
      );
      wheelDelta = 0;
      wheelGestureLocked = true;
      wheelTargetIndex = targetIndex;
      navigationLockUntil = performance.now() + (reducedMotion ? 0 : STAGE_ROTATION_DURATION * 1000);
      scrollToStep(targetIndex);
      scheduleWheelRelease();
    };

    const isModelCanvasTouch = (event: TouchEvent) =>
      event.target instanceof Element && Boolean(event.target.closest('.blueprint-canvas'));

    const onTouchStart = (event: TouchEvent) => {
      if (isModelCanvasTouch(event)) return;
      touchActive = true;
      if (scrollSettleTimer !== null) {
        window.clearTimeout(scrollSettleTimer);
        scrollSettleTimer = null;
      }
    };

    const onTouchEnd = (event: TouchEvent) => {
      if (isModelCanvasTouch(event)) return;
      touchActive = event.touches.length > 0;
      if (!touchActive) scheduleScrollSettle();
    };

    navigateToStepRef.current = scrollToStep;
    window.addEventListener('scroll', scheduleScrollSettle, { passive: true });
    window.addEventListener('scrollend', settleScroll);
    window.addEventListener('resize', scheduleScrollSettle);
    window.addEventListener('wheel', onWheel, { passive: false });
    window.addEventListener('touchstart', onTouchStart, { passive: true });
    window.addEventListener('touchend', onTouchEnd, { passive: true });
    window.addEventListener('touchcancel', onTouchEnd, { passive: true });
    settleScroll();

    return () => {
      navigateToStepRef.current = null;
      window.removeEventListener('scroll', scheduleScrollSettle);
      window.removeEventListener('scrollend', settleScroll);
      window.removeEventListener('resize', scheduleScrollSettle);
      window.removeEventListener('wheel', onWheel);
      window.removeEventListener('touchstart', onTouchStart);
      window.removeEventListener('touchend', onTouchEnd);
      window.removeEventListener('touchcancel', onTouchEnd);
      if (wheelIdleTimer !== null) window.clearTimeout(wheelIdleTimer);
      if (wheelReleaseTimer !== null) window.clearTimeout(wheelReleaseTimer);
      if (scrollSettleTimer !== null) window.clearTimeout(scrollSettleTimer);
    };
  }, []);

  const chooseLayer = (index: number) => {
    navigateToStepRef.current?.(index);
  };

  const activeLayer = LAYERS[activeStep];

  return (
    <main className="blueprint-shell" ref={shellRef}>
      <div className="blueprint-viewport">
        <header className="blueprint-header">
          <div className="brand-lockup">
            <img src="/brand/microduck-wordmark.svg" alt="Microduck" />
            <span>LIVE TWIN · 15 DOF · 250 MM</span>
          </div>
          <div className="drawing-title">
            <span>KINEMATIC RECONSTRUCTION</span>
            <h1>MICRODUCK // MOTION CORE</h1>
          </div>
        </header>

        <section className="parts-index" aria-label="Microduck anatomy sequence">
          <p className="hud-heading">
            <span>SCROLL SEQUENCE</span>
            <span className="sequence-stickers" aria-hidden="true">
              <img src="/stickers/bolt-blue-2.png" alt="" />
            </span>
          </p>
          <ol>
            {LAYERS.map((layer, index) => (
              <li key={layer.id}>
                <button
                  type="button"
                  aria-current={index === activeStep ? 'step' : undefined}
                  aria-pressed={index === activeStep}
                  className={index === activeStep ? 'layer-button is-active' : 'layer-button'}
                  onClick={() => chooseLayer(index)}
                >
                  <span>{layer.number}</span>{layer.label}
                  {index === activeStep && (
                    <img className="layer-sticker" src={layer.sticker} alt="" />
                  )}
                </button>
              </li>
            ))}
          </ol>
          <div className="layer-context" aria-live="polite">
            <strong>{activeLayer.label}</strong>
            <p>{activeLayer.detail}</p>
          </div>
        </section>

        <section className="live-data" aria-label="Live motion data">
          <div className="live-data-title">
            <span className="status-dot is-live" />
            <p>GAIT STREAM LIVE</p>
          </div>
          <dl>
            <div><dt>LOOP</dt><dd>0.81 S</dd></div>
            <div><dt>PHASE</dt><dd>{telemetry.phase}%</dd></div>
            <div><dt>HIP</dt><dd>{telemetry.hip > 0 ? '+' : ''}{telemetry.hip}°</dd></div>
            <div><dt>ROLL</dt><dd>{telemetry.tilt > 0 ? '+' : ''}{telemetry.tilt}°</dd></div>
          </dl>
        </section>

        <div className="model-stage" ref={hostRef}>
          {status !== 'ready' && (
            <div className="model-status" role="status">
              <span className="model-status-mark">MD</span>
              <p>{status === 'error' ? 'MODEL LOAD INTERRUPTED' : 'ASSEMBLING DIGITAL TWIN…'}</p>
            </div>
          )}
        </div>

        {inspection && (
          <aside
            className="inspection-tooltip"
            style={{ left: inspection.x, top: inspection.y }}
            aria-live="polite"
          >
            <div className="inspection-title"><ScanSearch aria-hidden="true" /> PART SKETCH</div>
            <span>{inspection.eyebrow}</span>
            <strong>{inspection.name}</strong>
            <p>{inspection.detail}</p>
            <small>{inspection.confidence}</small>
          </aside>
        )}

        <p className="interaction-hint">
          <span className="pointer-hint">SCROLL TO EXPLORE · ORBIT ON SPACE · POSE LEGS / HEAD</span>
          <span className="touch-hint">SWIPE TO EXPLORE · ORBIT ON SPACE · POSE LEGS / HEAD</span>
        </p>

        <aside className="source-badge" aria-label="Model source">
          <span>OFFICIAL SIMULATOR GEOMETRY</span>
          <a
            className="title-source-link"
            href="https://github.com/pollen-robotics/microduck_rl"
            target="_blank"
            rel="noreferrer"
          >
            MODEL SOURCE ↗
          </a>
        </aside>
      </div>

      <div className="scroll-track">
        {LAYERS.map((layer, index) => (
          <section
            key={layer.id}
            className="scroll-step"
            data-step-index={index}
            ref={(node) => {
              stepRefs.current[index] = node;
            }}
            aria-labelledby={`scroll-step-${layer.id.toLowerCase()}`}
          >
            <h2 className="sr-only" id={`scroll-step-${layer.id.toLowerCase()}`}>
              {layer.number} of 05 — {layer.label}
            </h2>
          </section>
        ))}
      </div>
    </main>
  );
}
