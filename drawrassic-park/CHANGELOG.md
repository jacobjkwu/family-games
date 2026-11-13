# Drawrassic Park — Changelog

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
