# Microduck (Pollen Robotics / Hugging Face) — visual reference catalog

Collected 2026-09-01. All Microduck stills and video frames live in this directory. Sources:
- Product page `https://pollen-robotics.com/microduck/` (Next.js site; assets under `/assets/microduck/…`)
- Press kit `https://pollen-robotics.com/microduck/press-kit/` (original full-res JPGs in `press/`, whole kit unzipped in `press/kit/`)
- Blog `https://pollen-robotics.com/microduck/blog/introducing-microduck/`
- Store `https://store.pollen-robotics.com/products/microduck` (Shopify CDN, 2400 px product shots in `store/`)
- GitHub `pollen-robotics/microduck` README media (`github/`), `pollen-robotics/microduck_rl` (**full MJCF + STL meshes of the real robot** — see `../cad/`)
- Press: TechCrunch (same as press_morning), Engadget, The Register, Interesting Engineering, Highleap (`press_ext/`)
- X/Twitter launch post `x.com/pollenrobotics/status/2092915032052879425` (video thumbnail only)

Video keyframes (1 fps) are in `frames/<video>/NNN.png`; contact sheets in `sheets/`.

Colourways (press kit, calibrated): Cream `#f7e6cb` (orange trim/beak, yellow-orange sole), Graphite `#6c6a68` (yellow trim/beak, lavender sole), Lavender `#bfa9cf` (yellow trim/beak, cyan eye ring), Sky `#a9dbe8` (orange trim/beak, yellow eye ring). Eye-ring colour = the contrasting accent, not the shell colour.

Published numbers: **25 cm tall, 14 cm wide, under 800 g (store: 780 g), 15 motors (Dynamixel XL330-M288-T visible on labels)**, front camera, 8x8 ToF LiDAR, 2 IMUs (body + head), articulated grasping beak, mic + speaker, 2 NFC antennas (head + beak), removable NP-F550 battery (2600 mAh, ~1 h), RK3566 + NPU, 1 GB RAM / 32 GB, Wi-Fi/BT. Mechanical files are NOT open-source hardware (press kit says so explicitly) but the RL repo ships the simulation meshes.

---

## Global anatomy (consistent across every image)

- **Head**: a "D"-profile loaf. Flat vertical front face (grey inset panel, slightly translucent-looking matte grey), dome top sloping down to a rounded rear, flat sides. Shell is a two-piece split: top shell (colour) + bottom shell (colour) with the **beak/trim colour band** sandwiched at the split line. Single **eye = camera**: 30 mm accent-colour ring (a cone/dish "noenoeil" part) with the M12 lens dead centre of the face. A small **pill-shaped dark window** to the viewer-right of the eye (ToF LiDAR / REC LED). Face panel is a separate grey part inset ~1 mm inside the shell lip.
- **Beak**: two flat plates in the accent colour. Upper beak is fixed to the bottom head shell (a lip ~10 mm deep all round the underside of the head). Lower jaw is a separate flat plate, hinged at the rear-sides of the head by two accent-colour **side brackets with 4 screws each** (visible on both sides near the rear of the head). Jaw opens ~25 mm at the tip. Under-side of jaw has a soft (TPU) pad; a soft "mouth top" pad sits opposite it.
- **Neck**: fully exposed stack of two black XL330 servos joined by grey folded-sheet brackets (neck pitch at the trunk, head pitch above), then head yaw + head roll inside the head. No cover. Cables visible.
- **Trunk**: rounded pill / soap-bar shell in shell colour, split **left/right** down the centre line (visible seam on the top front in `press_screentime`). One small round hole on each side of the top rear (button / LED / mic). Below the shell the hip mechanism is open: grey printed hip-roll clevis parts, two large flanged bearings, four black hip servos. **The NP-F battery hangs vertically at the rear of the trunk** (black block with rib, visible in back views) in a printed "power_support" cradle.
- **Legs (5 DOF each)**: hip yaw (in trunk, under shell) -> hip roll (grey clevis) -> hip pitch (black servo, outboard) -> knee (grey sheet shin) -> ankle (black servo sitting on the foot). The **thigh has a triangular cover plate** in shell colour with two screws; the shin is a bare grey 8 mm sheet with a big flanged bearing at the knee, exposed on the outside. Ankle servo is mounted vertically, its body forms the "shin" bottom.
- **Feet**: two-part. Top: accent-colour cap with a **triangular ankle bracket** (4 screws) rising from the middle and a slot on the top surface (roller-skate mount / NFC). Bottom: contrasting **rounded TPU sole**, ~13 mm thick, slightly larger than the cap. Foot is roughly 54 x 41 mm, rounded rectangle.
- **Fasteners**: countersunk/pan black M2 screws on servo horns (5-hole pattern), M2.5/M3 on shells. No visible vents; USB-C not visible externally (battery is the removable element; charger is external).
- **Finish**: FDM-printed shells (fine layer lines visible on close-ups, `press_stickers`, `store_*profile*`), matte. Grey structural brackets look like injection/printed grey plastic; the servos are Dynamixel black.

---

## Stills

| file | source | px | view | notes |
|---|---|---|---|---|
| `store/store_microduck-cream-standing-profile-left.jpg` | store | 2400x2400 | **pure left side view**, white bg | BEST side reference. Head loaf shape, beak sandwich, jaw side bracket (4 screws), exposed two-servo neck with "DYNAMIXEL XL330-M288-T" labels, trunk pill, battery ribs behind trunk, thigh triangle plate (2 screws), knee bearing, vertical ankle servo, foot cap + sole, sole slightly proud of cap. Pixel measure: head length = 0.42 of total height (graphite twin: 0.39); head sits pitched ~20 deg down. |
| `store/store_microduck-graphite-standing-profile-right-02.jpg` | store | 2400x2400 | pure right side view | Same as above mirrored, graphite/yellow/lavender. Shows the rear-of-head split line and that the jaw bracket sits at the rear-bottom corner. |
| `store/store_microduck-graphite-standing-back-three-quarter-right-02.jpg` | store | 2400x2400 | **rear 3/4** | BEST back reference. Shows: rear of head is plain rounded, trunk shell rear, black NP-F battery with two vertical ribs sitting in a cradle behind the trunk, hip servos, both thigh plates, knee bearings (large flanged bearing on shin outer face), ankle bracket screws, foot slot. |
| `store/store_microduck-sky-standing-three-quarter-left-02.jpg` | store | 2400x2400 | **front 3/4, jaw open** | BEST front-3/4. Jaw open ~25 mm; both beak plates flat with rounded corners; grey face inset; eye ring cone; ToF pill window right of eye; hip clevis parts; foot slot; neck labels. |
| `store/store_microduck-cream-sitting-three-quarter_1.png` | store | 2400x2400 (alpha) | front 3/4, SIT pose | Knees folded, feet forward showing soles; underside of thigh plate; knee servo horn; ankle bearing. |
| `store/store_microduck-lavender-sitting-three-quarter-left-04.jpg` | store | 2400x2400 | front 3/4, SIT, jaw open | Clear view of the two beak plates from below, hinge brackets, hip clevis geometry, foot cap vs sole colour split, thigh plate outline. |
| `store/store_microduck-4-colors-standing.png` | store | 1589x1589 | four robots, front 3/4, desk | Colourway reference; Reachy Mini poster on wall (no scale use). |
| `store/store_microduck-squad-sitting.png` | store | 1651x1651 | four robots, mixed poses | Front view of cream unit (eye centred on face, ToF at right); book stack (approx 22-24 cm tall) for scale. |
| `store/store_microduck-inside-the-box.png` | store | 1254x1254 | **true front (top-down flat-lay)** with NP-F550 battery, USB-C cable, gamepad | Scale reference: NP-F550 = 70.8 x 38.4 mm. Eye ring is exactly on the head centreline; ToF window to the right. Battery long side ~275 px, head width ~430 px -> ~110 mm apparent (flat-lay perspective; CAD says 92 mm). |
| `store/store_microduck-cream-standing-office.png` | store | 3060x3060 | front 3/4 close, desk | Best close-up of layer lines, jaw bracket 4-screw pattern, eye cone depth, ToF window shape (rounded slot ~8 x 4 mm), the small round hole on trunk top, two big grey hip parts, knee bearing. |
| `store/store_microduck-cream-standing-sleeping-room.png` | store | 3317x3317 | front 3/4 low angle | Same details, carpet. Shows trunk top opening where the neck servo enters (rectangular cut-out). |
| `store/store_microduck-lavender-standing.png` | store | 1023x1023 | front 3/4, jaw open | Small; colourway ref. |
| `store/store_microduck-sky-standing.png` | store | 1023x1023 | front 3/4 | Small; colourway ref. |
| `store/store_microduck-cream-playing-with-game-controller.png` | store | 3441x3441 | front 3/4 outdoors, second (graphite) unit behind | Woman kneeling with gamepad for scale (robot ~ knee height when kneeling). |
| `store/store_microduck-simulation-mujoco-office.png` | store | 1412x1412 | robot + MuJoCo screen | Shows sim twin; robot rear-3/4 small. |
| `press/press_closeup.jpg` | press kit | 2047x3640 | front 3/4 low angle, desk | Very sharp. Head loaf, eye cone, ToF pill, jaw bracket, neck servos + sheet brackets, trunk pill with seam, hip clevises, both feet. Keyboard behind (key pitch 19 mm) for scale. |
| `press/press_desk.jpg` | press kit | 4233x2380 | workbench, 4 partially assembled robots | **Detail gold**: bare head interior (lavender unit, camera module on a small PCB with lens holder visible through open face), trunk shells removed showing servo stack, spare foot caps and soles, XL330 servos, Xbox controllers (~150 mm wide) for scale. |
| `press/press_morning.jpg` | press kit | 4240x2650 | side/front 3/4 on desk | Clean profile-ish; second robot's bare head interior in foreground (yellow shell off, camera board visible). Also used by TechCrunch. |
| `press/press_kickabout.jpg` | press kit | 2768x1560 | three robots, side + front views | Sky unit side view with stickers; cream held by hand (scale: adult hand spans the whole head ~12 cm); graphite front view. Ball ~65 mm. |
| `press/press_stickers.jpg` | press kit | 2281x4057 | head close-up in hand | **Head detail**: layer lines, grey face panel inset, eye cone, ToF window, jaw side bracket. Thumb for scale (head ~ 2.5 thumb-widths). Also foot sole/cap junction. |
| `press/press_watching.jpg` | press kit | 2034x3617 | front 3/4 | Sharp; shows neck sheet bracket hole pattern, thigh plate screws, foot slot, ankle bearing. |
| `press/press_playtime.jpg` | press kit | 2003x3562 | rear 3/4 with person | Top of head (plain dome), battery rear, both thigh plates. |
| `press/press_screentime.jpg` | press kit | 2281x4057 | front, SIT | **Best pure front**: symmetric; eye centred; trunk centre seam; hip clevises; soles facing camera (rounded rect, slightly domed). |
| `press/press_bedroom.jpg` | press kit | 2193x3901 | wide, person for scale | Robot on floor next to sitting adult: robot height ~ shin length. |
| `press/press_playroom.jpg` | press kit | 2281x4057 | front 3/4 walking | Mid-stride; thigh plate swing; foot roll. |
| `press/press_walkabout.jpg` | press kit | 2357x3143 | front 3/4 | Head slightly pitched; stickers on shell. |
| `press/press_carried.jpg` | press kit | 2219x3947 | side, held in hand | Hand wraps the trunk: trunk width ~ palm width (~80 mm). Graphite/yellow/purple feet. |
| `press/press_team.jpg` | press kit | 2000x2667 | team photo, 2 robots | Robot height vs shoe: ~ 1x shoe length -> 25-28 cm. |
| `blog_scale-in-hand.webp` | blog | 1600x900 | front 3/4, hand on trunk | Scale: adult hand; robot head about a hand-length wide. |
| `blog_cover-microduck.webp` | blog | 1200x896 | (cover) | Marketing. |
| `blog_sim2real-poster.jpg` | blog | 1600x900 | sim/real split | Sim render matches CAD; real sky unit. |
| `launch-film-poster.jpg` | site | 1920x1280 | four people + robots outdoors | Scale vs people. |
| `pack-robot.webp` | site | 880x587 | illustration | In-box contents drawing. |
| `pack-dev.webp` | site | 880x587 | illustration | Dev pack: 3 spare XL330-style servos, 5 JST cables, 2 NP-F batteries, dual charger, 10 NFC tags, screwdriver, screws. |
| `pack-accessories.webp` | site | 880x587 | illustration | Accessory pack: **2 roller-skate modules** (yellow tray with 2 wheels each, clip onto feet), ball, laser pointer, NFC polaroid, 10 NFC tags. |
| `pack-charger.webp` | site | 880x587 | illustration | Dual NP-F charger + 2 batteries + USB-C. |
| `squad.webp` / `github/gh_readme_5.webp` | site / README | 1839x638 | 4 colourways cut-out | Side/3-4 views of all four. |
| `og_og-microduck-squad-v2.jpg` | site | 1200x630 | social card | Same squad. |
| `moves-portrait-alpha_posters_{walk,grab,drive,standup,sitstand,kickL}.png` | site | 800x1280 (alpha) | **CAD renders** (transparent) | Rendered from the same model as the MJCF; walk = front 3/4 standing; grab = crouched with jaw at floor; drive = front with roller-skates; standup = 3/4 rear. Clean silhouettes for tracing. |
| `gallery_*.webp` | site | 1012x1800 etc. | same shots as `press/` at lower res | Duplicates. |
| `gallery_*-poster.jpg` | site | 1280x720 | video posters | See frames. |
| `press_ext/engadget_intro.jpg` | Engadget | 1600x898 | = press_kickabout crop | |
| `press_ext/register_5293032.jpg` | The Register | 2000x1250 | = press_desk | |
| `press_ext/ie_cover.jpg` | IE | 1920x1080 | = press_kickabout | |
| `press_ext/hil_microduck.webp` | Highleap | 1206x418 | 4 colourways | Cut-outs. |
| `press_ext/hil_microduck-1.webp` | Highleap | 726x590 | lavender 3/4 + squad | |
| `press_ext/x_video_thumb.jpg` | X post | 1080x720 | launch-film frame | Bedroom scene, robot small. |
| `github/gh_readme_7.png` | microduck README | 2215x884 | sim vs real side view | Sim shows leg linkage clearly. |
| `team.webp`, `team-square.webp` | site | 1500x2000 | team | Scale only. |
| `stickers_*.webp`, `press/kit/STICKERS/*` | site | small | die-cut stickers | Not mechanical. `duck-head-mark*.webp` = head icon (silhouette reference for the head profile: flat face, domed back, beak lip). |

## Video frames (`frames/…`, sheets in `sheets/`)

| video | res / len | what it shows |
|---|---|---|
| `microduck-hero.mp4` (15 s, 1920x1080) | hero | sticker application on head (close-ups of the head shell top, eye cone); roller-skate clip-on being fitted to the foot (**skate module = yellow/orange tray with two wheels that clips under the foot cap, ankle stays**); skate park low angle. |
| `launch-film.mp4` (51 s) | launch film | bedroom walk; **get-up from lying on back** (frames 9-11); train-on-monitor; grab (jaw picks a sock, frames 17-19); four-robot line-up front view (43-48) — good for front silhouette of all four colourways; skate. Watermark "Prototype shown. Final product may vary". |
| `gallery_squad-standup.mp4` (33 s) | four robots stand up from lying, living room | many mid-transition poses; shows underside of feet and folded legs. |
| `gallery_balance-recovery.mp4` (13 s) | push recovery | sagittal-plane views mid-step. |
| `gallery_grab-and-carry.mp4` (10 s, portrait) | grab a sock, carry to box | whole-body crouch; jaw open at floor; NOTE jaw opens downward only (upper beak fixed). |
| `gallery_roller-skating.mp4` (11 s) | skating in living room | skates fitted; legs in "swizzle" motion. |
| `gallery_chorale.mp4` (12 s) | four robots, jaws moving | jaw range; head roll/yaw expressiveness. |
| `blog_sim2real.mp4` (24 s) | split sim/real | sim renders match physical robot: same foot/leg shapes. |
| `microduck-card.mp4` (13 s) | homepage card | recut of hero. |
| `github/gh_readme_4.mp4` (33 s) | README | roller-skating demo, living room. |
| `github/gh_readme_6.mov` (61 s, 1280x720) | README | **earlier prototype pair** (cream/yellow with purple eye and the cream/orange): head slightly boxier, small yellow "ear" nubs = jaw hinge brackets; shows standing, walking, head yaw, jaw open, sit. Legs identical to production. |
| `moves-portrait-alpha_*.webm` | site | CAD-rendered move loops on black (walk, sitstand, drive, grab, standup, kickL); clean orthographic-ish 3/4 renders for silhouette tracing. |

## CAD renders of the published MJCF (`../cad/renders/`)
`STAND_front.png`, `STAND_side.png`, `STAND_back.png`, `STAND_top.png`, `INIT_front.png` — orthographic, 4 px/mm, 50 mm grid, generated from `microduck_rl/robot_walk.xml` + STLs. These are exact geometry (alpha CAD; production shell colours differ but shapes match photos).

---

## Internals — what exists and what does not (appended 2026-09-03 by the src-internals lane)

Leif asked for "an new image covering the components of the microduck internals". Searched 2026-09-03
(full log with URLs and dates: `out/sources/internals.json` → `search_log`): MakerWorld 3250889, Pollen's
site/press kit/blog, both Pollen GitHub repos (zero image files in either tree), the HF
`mishig/microduck-anatomy` space (simulator meshes), the fanhao375 replica exploded drawings (MJCF-derived,
"unverified against physical hardware"), the bilibili "硬件架构拆解" video (a pre-ship analysis), and
EN/ZH web search. **No public photograph or diagram of the full internal layout exists** — units ship at
Christmas 2026. What DOES exist is two press-kit photographs of partially disassembled units, already in
this directory; the lane cropped them at 2x into `out/sources/internals/`:

| crop | from | shows |
|---|---|---|
| `real_desk_head_jaw_off.png` | `press/press_desk.jpg` (560,870)-(1260,1400) | lavender unit, lower beak removed: a green camera PCB standing vertically behind the face plate, the mouth-servo XL330 under it (label readable), the eye ring + M12 lens |
| `real_desk_trunk_shells_off.png` | `press_desk.jpg` (0,600)-(560,1330) | cream/mint unit, trunk shells off: two XL330 stacked, a small dark PCB with white silkscreen ("3V" legible) on the trunk plate below them, mint yaw2roll clevises with 22 mm flanged bearings; behind it an orange top head shell upside down showing its interior ribs |
| `real_desk_head_yawroll_stack.png` | `press_desk.jpg` (2450,180)-(3200,780) | graphite/orange unit lying down: the head yaw/roll servo pair with its printed brackets, cabling, and a graphite trunk shell |
| `real_desk_top_shell_interior.png` | `press_desk.jpg` (2400,120)-(2900,620) | inside of an orange top head shell |
| `real_morning_head_rear_open.png` | `press/press_morning.jpg` (3050,1100)-(4240,2000) | yellow bottom head shell seen from behind, the rectangular neck opening with the yaw/roll servo stack inside |

Our own labelled internals (see-through, shells-off, exploded, cable routes) are `INTERNALS.html`
(tools/gen_internals.py from out/sources/internals.json, renders by tools/internals_render.py).
