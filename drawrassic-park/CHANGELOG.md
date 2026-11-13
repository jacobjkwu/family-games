# Drawrassic Park — Changelog

## v3.30 (2026-11-13) — save schema s8 (unchanged)
- 🍱 Snack Bar: 37 foods as data entries in 4 groups — food (meat, steak, drumstick, fish, bug, lettuce, strawberry, corn, watermelon, apple, carrot, banana), treats (pizza, burger, donut, ice cream, popcorn, chocolate, party cake), silly food (super-hot chili, spider, giant mushroom, shrink candy, beans, triple coffee, brain-freeze slush, balloon gum, super-sour lemon, stinky garlic, sleepy tea, cactus) and magic food (ghost jelly, rainbow lollipop, twin cherries, lightning fruit, star fruit for 2 amber, mystery box).
- 22 effects, each a data entry that works on dinos and on people: 🌶️ red-hot head with steam and fire breath, running around screaming; 🕷️ spider dino with eight legs that webs visitors and dinos, then climbs a thread and hangs upside down; giant ×1.8 (stomps shake the screen) or tiny ×0.4; fart jumps; coffee zoom then a crash nap; frozen in an ice block; floating balloon that pops; sour squish; stink clouds that make people flee; instant sleep; cactus ouch-hops; see-through ghost that scares visitors; rainbow colours with a sparkle trail; two clones for 15 s; lightning that zaps shadow dinos; golden star (level up + shield); sugar dance; party (nearby dinos dance, visitors cheer); round belly after junk food; popcorn popping; banana peel left on the ground.
- Ways to feed: 🍖 Feed (quick normal food, favourite-aware), 🍱 Snacks on the dino card (any food, shows what it loves ❤️ and hates 🤢), and 🍱 Snack mode in the quick bar: pick a food, then tap a dino, a visitor or the ground (works with the controller cursor + A).
- Mischief: a nearby dino can snatch a snack in mid-air (dev panel: snSteal, default 15%); a snack on the ground starts a race between up to 4 dinos and 6 visitors; dinos steal visitors’ ice creams and burgers; sneaky visitors feed silly food; anyone can slip on a banana peel; spat-out food can splat a visitor.
- Each dino has a favourite food (hearts, spin, maybe a coin) and a hated one (spits it out), worked out from its id. Feeding combos (×3 and up) and a MEGA BURP at ×8 that blows visitors’ hats off. People refuse raw meat and sometimes tip a coin.
- Random events: 🍱 Snack rain (tap falling snacks, +1 coin each, the rest starts races) and 🌶️ Chili champion (3–4 dinos in a row eat chilies each round; tap one to give it milk; last one standing wins 8 coins).
- 🌿 Wild dinos now have an orange “🌿 Wild” tag (with trust hearts) and a dashed ring under them, and their card has an orange dashed frame.
- Controller fix: the D-pad no longer jumps to quick-bar buttons hidden behind an open dino card.
- Nothing new is saved (effects, clones, peels, ground snacks end with a reload). Save format unchanged (s8). Measured in desktop headless Chrome with 313 dinos + 83 visitors all under effects at once: AI 3.3 ms + draw 7.9 ms per frame (no effects: 2.2 + 5.8). Not tested on a real iPad or Xbox.

## v3.29 (2026-11-13) — save schema s8 (unchanged)
- 🐛 Fixed: tapping a wild dino showed no 🍖 Feed button (only 🎯 Catch), so those dinos could not be fed. The Feed and Pet buttons now show for every dino; Store/Release/Stats/Edit/Card stay park-only.
- 🍖 New feeding animation from the Feed button: a snack (🍖🥩🍗, 🐟 for swimmers, 🥬🍓🌽🍉🍎🥕 for plant eaters) flies in an arc into the dino's mouth, then chewing squashes, crumbs and chomp sounds, a sparkle, “+30 🍽️” and a pulsing tummy bar. Works while carried or in a fight too.
- 😵 A full dino shakes its head and the snack bounces off onto the ground, where another dino can eat it; a knocked-out dino gets the snack put down beside it. The button shows “· full”.
- ❤️ Feeding a wild dino gives it trust hearts (up to 3, shown over its head and on the button); each heart adds +12% catch chance (dev panel: fdTrust). Dev panel also gets fdSnack (tummy per snack).
- Dinos that find food on their own now chew too.
- Save format unchanged (s8); trust hearts and chewing are never saved. Not tested on a real iPad or Xbox.

## v3.28 (2026-11-13) — save schema s8 (unchanged)
- 🏆 Design contest (quick bar): a random theme (funniest, coolest, cutest, scariest, most colourful, biggest), pick one of your park dinos, three rival monsters from the Mix Factory, three judges flip score cards one by one with comments; scores come from the drawing itself (colours, size, dark/red, pink, length, special move…) plus a little luck. Prizes: 1st +10 coins +3 amber (with fireworks), 2nd +5, 3rd +2.
- 🃏 Trading cards (quick bar, or 🃏 on the dino card): a card drawn on the spot with a rarity frame (holo shine for epic and legendary), the drawing, level, rarity, food and movement, health/attack/stamina bars and the special move; ◀ ▶ through all park dinos; long-press to save.
- ✨ Doodle magic (quick bar toggle): draw on the park — a circle shields the dinos inside for 15 s (70% less damage, a bubble shows it), a zigzag calls magic lightning that hurts shadow dinos and bosses, a heart heals and wakes the dinos inside, a straight line makes a rainbow that cheers everyone up. 2 s between spells.
- 🎨 Draw & guess (quick bar, pass-and-play): one player draws a secret word (20 words in 4 languages) on a board with 6 colours, the other picks from 4 answers; right answers pay +2 coins each.
- 🎉 Welcome ceremony: every dino released through the gate gets a banner, a hatch flash, hearts and cheering visitors.
- Save format unchanged (s8). Not tested on a real iPad or Xbox.

## v3.27 (2026-11-13) — save schema s8 (unchanged)
- 🏭 Crazy Mix Factory (quick bar 🏭, and a button on the studio bar): parts are data entries with a painter, names and name syllables in 4 languages, and what they bring — 16 heads (shark, chicken, frog, owl, octopus, pumpkin, toaster, lightbulb, robot, T-rex, cat, duck, dragon, alien, pony, panda), 12 bodies (dino, ball, banana, burger, cloud, rocket, cactus, jelly, egg, teapot, ice cream, robot box), 10 legs, 9 tails (+none), 7 wings (+none), 9 hats/horns (+none). Mutations: 1–3 heads, 2–8 legs, long neck, size 80–125%, 10 colours.
- What a monster is: the name is built from syllables (e.g. shark + chicken legs + unicorn horn + body → 鲨鸡角兽), the special move comes from the head, a 20-point stats budget comes from what the parts bring, wings or rocket boots make it fly, fins or tentacles make it swim, the head decides food and voice pitch. 🎉 Make it! draws it into the studio and opens the release dialog with all of this filled in (still editable).
- Ways to make one: 🔧 build with ◀ ▶ 🎲 per slot; 🎰 slot machine with three STOP buttons; 🍲 cooking pot (up to 3 of 12 ingredients); ⌨️ words (part names in 4 languages, colours, “two heads”, “long neck”, “giant”, “tiny”); 🥚 capsule for 3 amber (rare / epic / legendary looks); 🙈 blind relay for 2–4 players with a covered preview and a reveal; 🧬 opens the Lab's gene fusion.
- 🤖 Merge 3 (quick bar or 🧬 tab): the three biggest park dinos on screen become one XL giant (tail, body and head cut from their drawings, combined health and attack, level +3) for 60 s, then split back where it stands. The giant is never saved; the three stay in the save the whole time.
- 🔀 Head swap random event: two dinos trade heads for 25 s; tap one to swap back early (+4 coins).
- The baked dino look now remembers its original drawing, so fusion and cut-ups use the clean drawing. Save format unchanged (s8). Not tested on a real iPad or Xbox.

## v3.26 (2026-11-13) — save schema s8 (new)
- **Schema change s7 → s8:** park dinos may carry rig markers `rig` {eye, hu, tu, leg} (sprite space 0–1), a voice pitch `voice` (0.5–2) and a chosen special move `special` (an arena skill key). On first start v3.26 copies save/s7 to save/s8; s7 stays untouched for v3.25 and older. Launcher: Copy progress both ways (s8 → s7 drops the three fields). Loaders clamp bad values. The Dino Box format is unchanged (box/s2), so a dino stored in the box keeps only its drawing and basics. Fixtures: drawrassic-park/fixtures/s7.json and s8.json.
- 🧸 Easy mode: ① pick one of the species shapes and a colour, ✨ paints the body with an outline, light/shade and a belly and stamps the eye; ② 18 parts placed automatically from the drawing's outline (back spikes, plates, sail, wings behind the body, horns, unicorn horn, frill, mohawk, crest, feathers, tail club, tail spikes, big teeth, claws, big eye, fire breath, antennae, crown); ③ 10 patterns that stay inside the body (spots, stripes, scales, stars, hearts, zigzag, polka dots, light belly, rainbow, sparkles) and 9 stickers (glasses, sunglasses, bow, blush, mustache, scar, bandana, star badge, flower).
- 🖌️ 15 brushes in both modes: round, marker, pencil, airbrush, calligraphy and magic stamps (scales, stars, hearts, leaves, flames, bubbles, fur, rainbow, sparkles, spikes); Apple Pencil pressure changes the size.
- 🛠️ Pro mode: 4 layers (behind, body, details, on top) with thumbnails, show/hide, move up/down and merge; shapes (rectangle, ellipse, triangle, star, heart, line; filled or outline); 🌈 gradient shading on what is drawn; HSV colour picker with recent colours and a 2nd colour; 💧 eyedropper; ✋ move with flip, ±15° turns and ±10% size; size and opacity sliders; zoom buttons and two-finger pinch zoom/pan; redo; 🦴 rig markers (eye, neck, tail, feet) that the park animation uses for the head and tail bands, the blinking eye and the foot line. The mode is remembered (drawrassic-park/studio/s1).
- 🎲 Random dino: a random unlocked species, colours, pattern, 1–3 parts and maybe a sticker, with a name.
- Setup: 🔊 voice pitch with a ▶ test, ✨ special move (any of the 15 arena skills or automatic; used in the arena), 📊 a 20-point stats budget (health, attack, stamina, stays full) turned into the dino's own stats.
- ✏️ Edit drawing on the dino card: loads the dino into the studio; ✅ Update keeps the dino (level, XP, place) and swaps its look, name and settings.
- ⋯ More: save the picture (long-press), import a photo into a layer, copy a dino code (DPDINO1:… with the picture, name and species) and paste a friend's code.
- Controller: D-pad left/right now stays on the same row when possible, so the top buttons stay reachable. Fixes: the quick bar no longer pushes the draw button outside the TV safe area (v3.23 regression); colour swatches are 44 px.
- Not tested on a real iPad (Apple Pencil pressure untested) or Xbox.

## v3.25 (2026-11-13) — save schema s7 (unchanged)
- 💥 New effects layer, built after Crab King Castle's recipe (hot core + coloured burst + smoke + ground ring + flash light + shake): pre-drawn glow, spark, smoke, ring, star, droplet and shard sprites, tinted and cached; additive blending; a pooled list of up to 700 effects (no garbage while playing); dynamic lights that matter most at night; screen flashes; a short hit-stop on big on-screen hits (at most once every 0.9 s); smooth sine-based camera shake.
- Every old particle now has a sprite look: glowing streak sparks, soft smoke dust, water droplets, flipping confetti, glowing stars and rings, shiny hearts, popping damage numbers with outlines. Big bursts add a glow, a ground ring and a light.
- Recipes for: hits and critical hits, knockouts (dust, ring, dizzy stars), level-ups (light pillar, rising stars, ring), hatching (shell shards, flash, sparkles), pick-ups, roars (sound-wave rings), shadow flashes, lightning strikes, boss and dark-boss entrances (flash, rings, smoke, freeze), magic.
- 🎆 Fireworks: new quick-bar action (also in the Mischief bar): rockets with trails burst into coloured star showers with glitter and light.
- Number panel: 💥 Effects (on/off, shake, flashes, freeze) and a 💥 Effects show button.
- Measured in desktop headless Chrome: 313 dinos + 100 visitors with an explosion and a critical hit every 0.15 s (≈350 live effects): draw ≈9 ms per frame. Normal play adds well under 1 ms. Not measured on a real iPad. Save format unchanged (s7).

## v3.24 (2026-11-13) — save schema s7 (unchanged)
- 🦖 Dino drawings are baked once when they load: a dark outline, light from above and a soft shade underneath (the original drawing is kept for analysis and fusion). Soft contact shadows for everything (one pre-drawn sprite).
- 🏔️ Far background: two layers of mountains (snow caps, shaded faces, haze toward the horizon), lit volcanoes with ridges and a glowing crater, shaded tree line. Clouds are pre-drawn with light tops and blue undersides, cross-fade to a night version, and float in front of the mountains.
- ☀️ Sky: deeper gradient, sun glow and slow rays, moon with craters and halo, twinkling coloured stars with sparkles, orange horizon at sunset.
- 🌿 Ground tiles: soft film grain, sun dapples, flower patches and pebbles in the meadow, haze near the horizon and a darker foreground. New painters for palms (ringed trunks, two-tone fronds, coconuts), jungle trees, berry bushes, ferns and boulders (faceted with moss).
- 💧 Lakes with a wet sand edge, depth colour, sky reflection, sparkles and moving foam; mountains you build get light and shadow sides, cracks and outlines; amber glows; coins shine.
- 💡 Light: warm sunset grading, soft god rays in the morning (sunny weather only), lamp posts and the visitor center glow at night, gentle vignette, floating pollen by day.
- 👥 People: outlined and shaded bodies and heads, eyes with whites and a shine up close, rosy cheeks, shiny hair.
- Number panel: 🎨 Picture quality (on/off, outline, shading, light, vignette, rays, ground texture); changes re-bake drawings and the ground live.
- Measured in desktop headless Chrome with 312 dinos + 103 visitors: draw 4.5–4.8 ms per frame (v3.23: 3.7 ms). Not measured on a real iPad. Save format unchanged (s7).

## v3.23 (2026-11-13) — save schema s7 (unchanged)
- 🎞️ Dino animation: the drawing is split into head / body / tail bands that move separately (head bob, tail swing, breathing), squash on landing, hop when petted, spin on level-up, roar at battle start, lean into lunges and recoil from hits, KO roll onto the back with kicking legs, belly drop and folded legs when asleep, blinking eyes found automatically on the drawing (✕ eyes when KO). Number panel: 🎞️ Dino animation.
- 💬 Line library: ~350 new kid-friendly lines, jokes, facts, riddles and visitor↔dino exchanges in all four languages, picked by context (weather, time of day, hunger, group, personality, nearby dino) with no repeats; rare golden lines. Visitors no longer talk over each other. Number panel: 💬 Lines & jokes.
- 🧰 Quick bar: 36 actions (tools, shop, arena, armies, sky, day/night, freeze time, speed, feed all, big roar, party, find/follow a dino, photo, data, settings…). ✏️ or a long press opens the editor: add, remove, reorder, 5 ready-made bars. Pages with ◀ ▶ when they don't fit. Stored in its own key drawrassic-park/toolbar/t1 (+ /bak).
- 📊 Park data: overview tiles with hungry/hurt alerts, history line chart (8 measures, a point every 20 s, 2 hours kept), dinos by group/rarity/food/movement, sortable dino list (tap to fly to a dino), visitors by type, staff by job and what they're doing, coins by source and per minute, and a diary of park news. History in its own key drawrassic-park/stats/h1 (+ /bak), not in the save.
- Fixes: shadow dinos at night could stop the drawing loop (new eye code needed a colour they don't have).
- Save schema unchanged (s7).

## v3.22 (2026-11-13) — save schema s7 (unchanged)
- 🎲 Random events, each a data entry (start / update / end / tap / draw). About every 2½ minutes (number panel: 🎲 Random events) one starts with a big banner and a sound; a panel at the top right (bottom right in portrait) shows the goal and time — tap it, or the red arrow at the screen edge, to jump to the action. No event starts during a boss fight, a disaster or in the arena. Nothing about an event is saved: a reload ends it and every dino goes back to normal.
- 🚨 Jailbreak: a dino escapes into the visitor plaza, visitors run screaming, the camera follows it; tap it 5 times in 40 s to lasso it back (+10 coins), otherwise it walks back by itself.
- 🛸 Flying saucer: a tractor beam lifts a dino; tap the saucer 12 times to knock it down (+15 coins, materials, and a lost alien now visits the park). Too slow? The aliens take the dino for a spin and bring it back wearing antennae.
- 💨 Fart storm: a dino ate too many beans; its stink clouds make visitors flee and other dinos gag; 3 taps of tummy pills end it with one mega fart that launches it into the air (+8 coins, amber).
- 😎 Superstar visit: a star, a bodyguard and two photographers stroll the park; make 3 of their wishes come true (see an epic or legendary / meat-eater / baby / super-happy dino up close, watch you pet or feed a dino nearby, eat ice cream at a cart). 3 wishes: five stars, +60 coins; fewer: less.
- 🥚 Mystery egg: a giant egg falls from the sky; tap 8 times to crack it (or wait 25 s): a rare species, or a funny mix of two species with a mixed-up name.
- 🌀 Time rift: a portal brings knights, cavemen, a mammoth, a sabre-tooth cat and a robot dino; tap them to say hi (+5 coins each); when the rift closes they are pulled back in.
- 🤧 Dino flu: sneezes blow visitors off their feet and spread the cold to nearby dinos; tap sick dinos (or let a hired vet) give them medicine.
- New visitor types for events (alien, knight, caveman, superstar, bodyguard), people can be thrown by a sneeze, 63 new lines translated into English and French. Settings: 🎲 Random event now. Number panel: event timings and a ▶ button for each event. Controller: the stick cursor + A works for every event tap. Save format unchanged (s7).

## v3.21 (2026-11-13) — save schema s7 (unchanged)
- 🖥️ Adaptive resolution for the park and the arena: when the time between frames stays above 20 ms (under ~50 fps) for a second, the canvas is drawn at 15% lower resolution, down to 50%. The cached background stays sharp; taps and the controller cursor still land in the right place.
- Each step is checked: if frames don't get faster within 1.5 s (the slowness is in the game logic, or the iPad is capped at 30 fps in Low Power Mode), the step is undone and not retried for 30 s (then 60, 120… up to 10 min). After 6 s of smooth frames the resolution goes back up one step; if that makes it slow again, it steps back down and waits.
- The arena's old one-way switch to 70% is replaced by the same controller, so it can recover too.
- 📈 FPS overlay shows the current resolution. Number panel: new 🖥️ Adaptive resolution group (on/off, lowest resolution, step, slow/fast thresholds, timings).
- Tested in desktop headless Chrome with a simulated GPU-bound load (25 ms per megapixel: 33 ms → 70% resolution, 19 ms) and a simulated logic-bound load (undone after the check). Not measured on a real iPad. Save format unchanged (s7).

## v3.20 (2026-11-13) — save schema s7 (unchanged)
- 👥 16 visitor types, each a data entry (age, speed, outfit, hat, props, favourite actions, lines): tourist, family, kid, teen, grandparent, photographer, jogger, scientist, artist, kid in a dino costume, tour guide, chef, firefighter, builder, police officer, astronaut. Every person also gets a random skin tone, hair style and colour, body size, glasses or sunglasses.
- New drawing and animation: two-part legs with knees and swinging arms, body bob, running lean, smooth start/stop and turning, blinking, head turns. Poses: photo (with flash), selfie, wave, point, jump/cheer, roar, take notes, sketch, eat, panic. Grandparents use a cane and sit on benches, people go into the restrooms and come back out, wave from the lookout tower, cheer at the carousel, and hold the ice cream or burger they bought. Far or crowded people are drawn in a simpler form.
- Sensible walking: people plan a route around ponds and mountains instead of walking through them (checked: 0 of 590 frames with anyone in water, 66 people at ×4 speed), never pick a spot in the water, step around dinos on the way, don't visit dinos that are fighting, and back away when a fight starts near them.
- Staff: the n-th ranger you hire has a job: 🧑‍🌾 ranger (does everything), 🧑‍⚕️ vet (heals hurt dinos, wakes knocked-out ones fast), 🪣 keeper (feeds hungry dinos), 🔦 guard (fights shadow dinos harder, patrols near the wall at night), 🧹 cleaner (picks up amber left on the ground for you). The Shop shows the team and who the next hire will be. The save still stores only how many are hired: save format unchanged (s7).
- 64 new lines in Chinese, translated to English and French (Traditional Chinese by conversion).
- Number panel: 👥 Visitors group (most visitors at once, walking speed) and a 👥 +50 visitors stress button. Measured in desktop headless Chrome: 314 dinos + 139 visitors, AI 2.0 ms + draw 3.7 ms per frame.

## v3.19 (2026-11-13) — save schema s7 (unchanged)
- 🎮 Controller support (Xbox controller in Edge on Xbox, or any standard gamepad). One rule everywhere: the left stick moves a cursor and A taps or holds where it points, exactly like a finger (pick up and carry dinos, rub to pet, hold for terrain, draw); the D-pad moves a big yellow focus ring between buttons, A presses it, B goes back.
- Park: LB/RB change tool, right stick or LT/RT look around (the cursor at the screen edge also scrolls), X ✏️ draw a dino, Y or Menu ⚙️ settings (pause), View ❓ help. Menus and dialogs: D-pad or stick to move, A choose, B back/close, LB/RB switch tabs, right stick scrolls, ◀ ▶ change sliders. Drawing (touch-first, but playable): stick cursor + hold A to draw, X undo, Y pen/fill/eye/eraser, LB/RB colour, LT/RT size, B back to the park. Arena: A cheer at the cursor, X speed, Y/Menu pause.
- ⚔️ Army battle with controllers: each controller presses A to join (player 1 red, then player 2 blue; touch players can mix in); with a controller the two halves sit side by side facing the TV instead of being turned toward the iPad's sides. Each player has their own focus ring; B removes the last dino, View switches side, Y leaves. In the battle: A ⚡ charge, X 🛡️ defend, B 🌟 super move, Y/Menu pause. A 3rd or 4th controller is told the two seats are taken. Rumble on powers and at the end.
- On-screen hints follow the last input: after a controller press a bar shows A/B/X/Y in their colours (A green, B red, X blue, Y yellow); touching the screen hides the cursor, ring and hints. If a controller in use disconnects, the arena pauses and the park opens ⚙️ settings.
- Xbox Edge is asked for raw controller input (`navigator.gamepadInputEmulation='gamepad'`), so Edge's own mouse cursor is off in the game and B no longer means "browser back". Pressing both sticks (L3+R3) gives the controller back to Edge's cursor, and again to return.
- 📺 TV size: on Xbox (or Settings → 📺 TV size: Auto / On / Off) menus, buttons and dialogs are zoomed (×1.75 at 1080p: body text 28 px, coin/amber numbers 40 px) and kept inside a 5% safe margin; canvases are not zoomed. ⛶ Full screen button on the start (help) screen and in Settings.
- Launcher: works with a controller (focus ring, A choose, B close dialogs) and is zoomed on Xbox.
- Number panel: new 🕹️ Controller group (stick dead zone, cursor speeds, camera speed). Saved in the same config key (`config/c1`); an older version that saves the panel drops these four values (they return to defaults). Save format unchanged (s7).


## v3.18 (2026-11-13) — save schema s7 (unchanged)
- 🌐 Four-language UI for the whole game (English, Français, 简体中文, 繁體中文): menus, buttons, shop, lab, arena, army and online dialogs, sky panel, number panel, ticker messages, signposts, floating text and the help screen. The dinos' speech, jokes and riddles (397 lines) are translated too; species names use the 141-species name table.
- Language buttons in the help screen and in ⚙️ Settings; the choice applies at once (no reload) and is stored in the shared settings key, so the launcher and every version use the same language. First launch picks from the device language (zh-TW/HK/MO/Hant → 繁體, other zh → 简体, fr → Français, else English).
- Dino names you typed are never translated. Save format unchanged (s7).

## v3.17 (2026-11-12) — save schema s7 (unchanged)
- 🌐 Online army battle (Arena → 🌐 Online battle): ➕ Create a room shows a 5-character code (no look-alike letters) and 📋 Copy link (`?room=CODE` opens the game and joins). The friend types the code or opens the link. Each player builds their own army on their own screen and sees the friend's progress; when both are ✅ ready, the battle starts.
- The room creator (player 1, red) runs the battle and sends the fighters' positions about 15 times a second; player 2 (blue) sends only their power buttons (⚡ 🛡️ 🌟). Both see the same result. Rematch is started by player 1.
- Connection status always shows at the top. Wrong code → "room doesn't exist"; a third player → "room full"; different game versions → "Your friend is on vX, you're on vY"; a dropped connection reconnects by itself (up to 10 tries); a player leaving is shown to the other.
- Uses WebRTC through PeerJS 1.5.4 (copy in `vendor/peerjs.min.js`, MIT) and its free public broker (0.peerjs.com): no uptime guarantee, and without a TURN relay some networks (strict NAT, some mobile or school networks) won't connect. Online play doesn't work in the claude.ai artifact copy.
- When the game is opened with a room link, the start-up backup reminder is skipped (the empty-storage prompt and the 💾 red dot still work). Save format unchanged (s7).

## v3.16 (2026-11-12) — save schema s7 (unchanged)
- ⚔️ Army Battle (Arena → ⚔️ Army battle, 2 players): players sit top/bottom in portrait or left/right in landscape; each half of the screen is turned to face its player. Each player taps dinos (24 species) to build an army with 100 points (common 5, rare 8, epic 12, legendary 20; up to 30 dinos), or 🎲 random army, then ✅ Ready. Both players can touch at the same time.
- In the colosseum the red and blue armies line up and fight. Each player has three powers on their side: ⚡ Charge (faster and +40% damage for 4 s, 10 s cooldown), 🛡️ Defend (half damage for 4 s, 12 s cooldown), 🌟 Super move (every dino uses its special move now, 20 s cooldown).
- Result: ⚔️ Rematch, 🔄 Swap sides, 🏞️ Back to the park. Army battles use generated dinos, not park dinos, and give no rewards. Save format unchanged (s7).
- Next multiplayer step: online army battles by room code.

## v3.15 (2026-11-12) — save schema s7 (unchanged)
- The ☀️/🌙 button now opens 🌦️ Sky & powers (it shows the current weather or disaster): time of day, weather and disasters.
- Weather: sunny, rain (bushes regrow twice as fast), thunderstorm (lightning strikes stun dinos nearby), snow (dinos get hungry faster), wind, fog. Rain, storms and snow send visitors home. Optional 🔄 automatic weather changes (every 1.5–3 min, on by default).
- Disasters: earthquake (shaking, cracks, stunned dinos), volcano (red sky, lava fountain, lava bombs and lava pools), meteor shower (12 meteors with warning circles), flood (water rises, dinos move up and slow down), tornado (lifts dinos and drops them, hurts shadow dinos), ice age (blizzard, everyone slowed). Dinos can be knocked out but never lost; the 🛡️ cheat in the number panel blocks the damage. Each disaster leaves a material gift. Optional ⚠️ random disasters (rare, off by default).
- The automatic choices are stored in localStorage `drawrassic-park/weather/w1`; weather itself is not saved. Save format unchanged (s7).

## v3.14 (2026-11-12) — save schema s7 (new)
- **Schema change s6 → s7:** adds hired rangers `rangers`; decorations can now be facilities, which v3.13 and older don't know (they would drop them), hence the new format. On first start v3.14 copies the s6 save to `save/s7`; s6 is untouched for v3.13. Launcher: Copy progress both ways (s7 → s6 drops rangers and facilities).
- 🏗️ Facilities tab in the Shop (paid with coins, placed like decorations, half refund when removed): ice-cream cart and burger stand (visitors buy food: +coins), restrooms, bench, lookout tower, dino carousel (animated), dino clinic (heals dinos nearby, knocked-out dinos wake sooner), auto feeder (feeds hungry dinos nearby), lamp post (its light hurts shadow dinos at night), ranger hut (+2 ranger places).
- Visitors: the park rating (dinos by rarity + facilities) decides how many visitors come by day (up to 40). Each pays a 1-coin ticket, walks to dinos and facilities, says things, takes photos, buys food, and leaves at night or when shadow dinos come.
- 🧑‍🌾 Rangers (hire for 30 coins; 2 places, +2 per ranger hut, max 10): they feed hungry dinos, break up fights, wake knocked-out dinos and chase shadow dinos with a flashlight at night.
- The park title shows visitors and rangers (👥, 🧑‍🌾).


## v3.13 (2026-11-12) — save schema s6 (new)
- **Schema change s5 → s6:** adds materials `mats` {id: count}, the Fusion Book `book` (name, parents, species, date, small picture for the newest 60) and a per-dino fusion count `fz`. On first start v3.13 copies the s5 save to `save/s6` (s5 is left untouched for v3.10–v3.12). Launcher: Copy progress both ways (s6 → s5 drops materials, book and fusion counts).
- 10 materials: 🦴 fossil bone and 🪶 ancient feather (sparkly finds in the Wild Lands — tap them — and from catching wild dinos), 🍃 magic leaf (plant-eaters grazing bushes), 🔮 shadow shard (defeated shadow dinos, collected by themselves after 12 s), 🐉 dino scale (arena and Boss Altar wins), and one boss material per boss (🌋 lava core, ❄️ ice crystal, ⚡ thunder plume, 👑 shadow crown, ☠️ dark wing bone) from park boss fights and Boss Altar wins.
- 🧪 Lab (new toolbar button) with four tabs: 🎒 Materials (counts and where to find each), 🧪 Make (energy juice: all dinos full stamina, less hungry; XP candy: +40 XP for the 5 lowest-level dinos; mystery egg: a rare/epic/legendary species; legend egg: a legendary species; dark egg: a pitch-black legendary dino), 🧬 Fusion (pick a head dino and a body dino, see a live preview, fuse for 🔮×2 🦴×2; both parents stay), 📖 Fusion Book (every fusion with picture, parents and date).


## v3.12 (2026-11-12) — save schema s5 (unchanged)
- 💬 Talk and tapping a dino: 30% of the time it tells a riddle, then the punchline 2.6 s later (a nearby dino often laughs or groans).
- New lines for each dino group (meat-eaters, raptors, long-necks, horns, armour, duck-bills, flyers, swimmers) and for 40 species.
- Lines for what is happening: tired, stunned, slowed, a boss in the park, hurt, legendary or rare species, a dino whose stats were changed.
- Every 14–26 s two dinos near each other on screen have a short conversation.
- Lines are in Chinese, like the existing dino lines; they will be translated in the four-language version.
- Save format unchanged (s5).

## v3.11 (2026-11-12) — save schema s5 (unchanged)
- 👹 Boss Altar in the Wild Lands' Boss Arena (a glowing ring and a "tap the altar" sign mark it; also in Settings). Pick one of the 5 bosses (Shadow Rex, Thunderwing, Magma Ankylo, Frost Spino, Mutant Dark Quetzalcoatlus) and up to 6 park dinos (⭐ picks the strongest 6), then fight in the colosseum.
- The boss's health and attack scale with the team you bring (the Dark Quetzalcoatlus is the hardest). Each boss uses its own 3 moves, built on the arena's move types; stuns on a boss last at most 0.4 s.
- Win: the boss's amber and coins, +60 XP for every dino in the team. Lose: +25 XP. Result screen: ⚔️ Again or 👹 Other boss.
- Save format unchanged (s5); v3.10 and v3.11 share the same park.

## v3.10 (2026-11-12) — save schema s5 (new)
- **Schema change s4 → s5:** each dino can carry its own stats `st` {hp, atk, sta, hun} and its current stamina `sta`. On first start v3.10 copies the s4 save to `save/s5` (s4 is left untouched, so v3.9 still plays its own save). Launcher: Copy progress works both ways (s5 → s4 drops the per-dino stats); Recover saves now restores into s5. The Dino Box (`box/s2`) is still shared.
- 126 more species (141 in all), each a real dinosaur, pterosaur or sea reptile with names in 4 languages, made by a shape generator from 20 body types. The draw screen has 📚 All dinos: a picture grid with group tabs (meat-eaters, raptors, long-necks, horns, armour, duck-bills, flyers, swimmers). Wild Lands and arena challengers use every species; new species use their body type's arena move.
- Rarity per species: common, rare, epic, legendary. Rarer species have higher stats, appear less often in the Wild Lands (★ marks above rare wild dinos, news when a legendary appears) and are harder to catch.
- Stamina: fighting and running use it, rest and sleep refill it; a tired dino (😮‍💨) can't attack and moves slower. Health, attack, stamina and hunger speed show on the dino card; 🎛️ Stats on the card sets them for that one dino (and its current health, hunger and stamina).
- 🎛️ Number panel (Settings, long-press the park title, or `?dev=1`): every stat, rarity, boss and wild-dino number, per-species stats and rarity, cheats (can't get hurt, endless stamina, game speed ×0.25–×4, +coins, +amber, unlock blueprints, boss now, night now, FPS), named presets, export/import as code. Stored in localStorage `drawrassic-park/config/c1` (+ `/bak`) and `drawrassic-park/presets/c1`. A MOD tag shows when numbers differ from normal.
- Bosses: from night 5 a boss comes every night. From night 9 the Mutant Dark Quetzalcoatlus rises from the Boss Arena and flies into the park: Spear Beak (jab, 3 s stun), Ground Drill (beak bursts out of the ground under up to 3 dinos and leaves them at 10% health, slowed), Wing Gale (everything in front of it, as far as its own length, is slowed and pushed). Both bosses can be out at once, each with its own health bar. Settings: ☠️ Summon the Dark Quetzalcoatlus.


## v3.9 (2026-11-12) — save schema s4 (unchanged)
- Night bosses: each night from 1 to 10 has a 30–75% chance (40% after night 10) that a boss comes 8–16 s after dark. Shadow Rex (Quake Roar, Tail Sweep, Shadow Call), Thunderwing (Lightning, Dive Bomb, Thunderstorm), Magma Ankylo (Lava Pools, Iron Shell, Meteor Slam), Frost Spino (Frost Breath, Icicle Rain, Winter Howl). Area attacks show a warning circle first. Boss HP bar at the bottom of the screen; stuns on bosses last at most 0.35 s. Defeating one gives coins, amber and XP to dinos nearby; at sunrise it runs away. Settings: 👹 Summon a boss now.
- Wild Lands: up to 6 wild dinos roam past the wall. Tap one, then 🎯 Catch: throw the net when the ring matches the dashed circle (3 nets; higher-level dinos are harder). A caught dino walks into the park, or goes to the Dino Box if the park is full. Wild dinos are never saved; dragging one over the wall sends it back. Settings: 🌿 More wild dinos.
- New text for these features in all four languages.

## v3.8 (2026-11-12) — save schema s4 (unchanged)
- Xbox pairing: Google sign-in fails on Xbox Edge (the redirect result is lost to cross-site storage blocking). A device paired in the Game Hub (anonymous Firebase sign-in plus a 6-letter code typed on the signed-in iPad) now uses the owner's cloud saves: the owner uid comes from localStorage `family-cloud/state.owner`. Settings shows a link to the Game Hub for pairing.

## v3.7 (2026-11-12) — save schema s4 (unchanged)
- Self-healing loader: dinos, eggs and Dino Box items with an id already seen are dropped on load (a v3.5 double import saved every dino twice with the same id; a backup taken afterwards carried the copies too). A toast says how many were removed, and the cleaned park is saved.

## v3.6 (2026-11-12) — save schema s4 (unchanged)
- Fixed: two imports running at once (tapping “Load this backup” twice) both cleared the park and then both added their dinos, so every dino appeared twice and was saved that way. Park reloads now run one after another, the import button is locked while importing, and a cloud restore can't start twice.

## v3.5 (2026-11-12) — save schema s4 (unchanged)
- ☁️ Automatic cloud backup with Firebase (Google sign-in + Firestore), only on the family games website (https://jacobjkwu.github.io/family-games/drawrassic-park/). In the claude.ai artifact the feature is off and Settings links to the website.
- Uploads every 2 minutes while someone is playing, and when the page is hidden. Each drawing is uploaded once (`users/{uid}/imgs/{hash}`); park snapshots are kept hourly (last 48) and daily (last 30) under `users/{uid}/games/drawrassic-park/snaps`.
- When another device has newer progress, the game asks whether to load it; the local park is backed up first (`save/s4/rescue-<time>`). Settings: Upload now, Restore from cloud (list of backups), Sign out. A device with empty storage offers "Restore from cloud".
- A cloud upload counts as a backup, so the 💾 red dot and reminders stop while cloud backup works.

## v3.4 (2026-11-12) — save schema s4 (unchanged)
- Backups outside the browser: a 💾 button in the top bar copies the full backup code (park, drawings, Dino Box) to the clipboard in one tap, to paste into Notes. "Last backup" shows in Settings (stored in localStorage `drawrassic-park/backup`).
- The 💾 button gets a red dot when a backup is due: progress worth keeping and no backup for a day, or a new dino, Dino Box item or level-up since the last backup and over an hour since it. On start, a reminder dialog offers a one-tap backup.
- Empty-storage guard: a device with completely empty storage first asks "Import my backup" or "Start a new park".
- Background: on 2026-11-13 the iPad's game storage was replaced by an empty one after the artifact's sharing was switched public → owner-only → public (see family-game-studio/data-safety-rules.md). The old progress could not be reached from the game.

## v3.3 (2026-11-12) — save schema s4 (unchanged)
- Fixed a save-loss bug present since v2.3: if IndexedDB took over 2.5 s to open, the game started a new park, and when storage finished opening, autosave wrote that new park over both the save and its `/bak`. Now the game waits up to 15 s; if storage still hangs, it saves nothing and asks you to reopen. A session that started a new park never overwrites a save it didn't load.
- Daily backups of the save and the Dino Box (`save/s4/day-<date>`, `box/s2/day-<date>`), last 7 days kept.
- Launcher: new 🛟 Recover saves tool. It lists every save still on the device (current, backups, damaged copies, older versions' saves, small-storage saves), restores one after backing up the current park, and puts drawings that are in neither the park nor the Dino Box into the Dino Box (names and levels recovered from older saves when found). A game that finds no save but sees drawings offers to open it.

## v3.2 (2026-11-12) — save schema s4 (unchanged, shares the v3/v3.1 save)
- Fixed: in v3.1 the arena kept opening by itself. The arena's start function had the same name as the park's "two dinos start a fight" function, so every park fight opened the arena (and park fights stopped working). Renamed; park fights work again.
- Arena: choose fighters yourself (tap a card to pick a dino, a random dino or a wild challenger; picking a dino already in the fight swaps them), or keep random.
- New 👑 King of the Arena mode: a free-for-all with 16, 32, 64 or all park dinos (up to 150), with a remaining-dinos counter, a knockout feed, a crown for the winner (+50 XP, +10 coins) and a most-knockouts list. With many fighters, effects, sounds and drawing are scaled down to stay smooth.

## v3.1 (2026-11-13) — save schema s4 (unchanged, shares the v3 save)
- New ⚔️ Arena button in the toolbar: picks random park dinos (wild challengers fill in if there are too few) for 1v1, 4-way brawl, 3v3 teams or an 8-dino royale in a colosseum. Each species has a special move (Mega Bite, Pounce, Horn Charge, Tail Spikes, Dive Bomb, Sonic Honk stun, Venom Spit, Sail Flame…). Effects: sparks, glows, shockwaves, dust, debris, afterimages, damage numbers, crits, combos, hit-stop, screen shake, zoom, K.O. slow motion and confetti; tap to cheer for a short power boost. Winner gets +30 XP, others +6, and you get +5 coins. Arena text is in English, French, Simplified and Traditional Chinese.

## v3 (2026-11-13) — save schema s4
- The park is 4 screens wide: visitor plaza, meadow, forest, Great Lagoon (with a Mosasaurus) and the Wild Lands with a Boss Arena. Drag the ground to look around; mini map at the top.
- Terrain tool: hold to dig a crater, make a lake or raise a mountain (the longer you hold, the bigger); 🧹 smooths them away.
- Performance: only on-screen dinos are drawn, off-screen dinos think every 4th frame, simpler drawing when many are visible, spatial grid for neighbour checks, shared images. Settings has an FPS meter and a +100 test dinos button.
- **Schema change s3 → s4:** adds `terrain`; old positions move into the meadow; a Mosasaurus is gifted once. s3 stays untouched.

## v2.3 (2026-11-13) — save schema s3 (IndexedDB)
- Fixed "storage full" errors. Safari gives each website only about 5 MB of localStorage whatever free space the iPad has; drawings are large and v2.2 also kept a backup copy, so saves hit that limit.
- **Schema change s2 → s3:** same fields, but the save, Dino Box and drawing draft now live in IndexedDB (database `drawrassic-park`, keys `save/s3`, `box/s2`, `draft/s2`), with each drawing stored once by content hash (`img/<hash>`). s2 and s1 stay untouched in localStorage.
- Autosave every 5 s. Settings shows how much storage is used.
- Launcher: reads and copies IndexedDB saves, and has a Storage section to delete old copies (backups, damaged-save copies, old versions' saves) after confirmation.

## v2.2 (2026-11-12) — save schema s2
- Each dino can have only one baby in its life (both parents use up their one baby when they lay an egg).
- Safer saves: keys are now prefixed `drawrassic-park/`, the save has its own schema (s2, key `drawrassic-park/save/s2`), every write keeps the previous save as `/bak`, damaged saves fall back to the backup and are kept as `/broken-<time>`.
- **Schema change s1 → s2:** adds `kids` per dino. s1 (v1–v2.1, key `drawrassic_park_v1`) is migrated on first launch and left untouched, so v2.1 still plays its own save.
- ⚙️ Export/Import backup code; asks Safari to keep storage (`navigator.storage.persist`).
- Version badge (v2.2) and "Switch version" in Settings. The artifact is now a launcher holding every version (index.html + versions.json + each version file); it can copy progress between versions with a backup and undo.

## v2.1 (2026-11-12) — bug fix
- Fixed: once the park had 20 dinos, "Open the gates!" silently did nothing (the warning was hidden behind the window).
- Park dino limit is now a setting (⚙️). Default: no limit. Options: 20, 50, 100, 200.
- New 📦 Dino Box: saves dinos without putting them in the park. If the park is full, a new dino goes to the box automatically. Box dinos can be released, redrawn or deleted.
- 💾 Save button on the drawing screen and on the setup window.
- 📦 Store button on a park dino's card moves it into the box.
- The drawing in progress autosaves, so a refresh or closed tab doesn't lose it.
- Day/night: 🌗 button switches day and night instantly. ⚙️ Settings can pick Day, Sunset, Night or Dawn and freeze time.
- With many dinos, each dino is drawn more simply to keep the game smooth.

## v2 (2026-11-12)
- Night raids: small shadow dinos (Shadow Raptor, and the tougher Shadow Brute) sneak in at night and attack your dinos. Meat-eaters and brave/fierce dinos fight back; calm plant-eaters run. Tap a shadow to blind it with a flash. They burn away at sunrise.
- Coins: every defeated shadow drops coins (Raptor 2, Brute 5). Tap to collect, or they collect themselves after 12 s.
- Dino Blueprints: new Shop tab. Spend coins to unlock 8 new species to draw: Pachycephalosaurus 4, Parasaurolophus 5, Dilophosaurus 6, Ankylosaurus 7, Spinosaurus 9, Carnotaurus 9, Quetzalcoatlus 10, Mosasaurus 12.
- Funny lines (in Chinese): dinos chat on their own, say something when tapped, and have a 💬 Talk button. Lines depend on species, diet and situation (for example, the T-Rex Minecraft line).
- Sound effects: dino babble voices, burps, snoring, a level-up fanfare, a boing when dropped, giant footsteps, pterosaur screeches, swimmer bloops, a spooky night gong, poofs, zaps and coin jingles, plus crickets at night, birds by day and volcano rumbles.
- Saves now keep coins, unlocked blueprints and the night count. v1 saves load fine.

## v1 (2026-11-12)
- Draw a dino (pen, fill, eye stamp, eraser, undo, 7 guide templates), choose diet, movement, size and personality, then release it through the park gate.
- Park simulation: hunger, feeding, growth to level 10, hunting critters and plant-eaters, dino-vs-dino battles, knockouts instead of death, eggs and hatching babies.
- Touch controls for iPad Safari: tap for stats, drag to carry, rub to pet. Amber currency and a decoration shop. Day/night cycle. Auto-save in the browser.
