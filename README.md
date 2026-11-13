# Family Games

Games built with Claude: https://family-games-hub.vercel.app/ (main) · https://jacobjkwu.github.io/family-games/ (GitHub Pages, old address)

Vercel deploys this repo on every push to main. GitHub Pages stays up as the old address and fallback. Each address is a separate origin with its own browser storage, so moving a device means backup → add the new icon → restore → check → delete the old icon. Keep GitHub Pages running: frozen version files link back to it.
- `vercel.json`: `trailingSlash: true` (so `/game` becomes `/game/` and relative paths like `../shared/` work) and `Access-Control-Allow-Origin: *` (copied community games load their images with CORS, as on GitHub Pages).
- `games.json` links our own games with relative URLs (`goat-mayhem/`), so the hub stays on whichever address it was opened from. The friend-request email links to the hub on the address the friend used (`MAIL.hub` in `shared/family-cloud.js`).

- `index.html` + `games.json`: the Game Hub (touch, Xbox controller, mouse, keyboard). Edit `games.json` to add a game or bump its latest version; the hub sorts it onto shelves by `category`, `input` and `genre`.
  - Layout (TV style): a hero card (▶ Continue the last game, or today's pick from our own games), then horizontal shelves: Recently played, My favorites, Our own games, Play with a controller (on Xbox or once a controller is used), one shelf per community genre (games that suit the device first), and keyboard-only games last.
  - Controller: D-pad/left stick move (each shelf remembers its position), A play, B back (start of shelf → hero), X search, Y favorite, LB/RB page through a shelf, Menu language & settings. A detail bar shows the focused game's full description. Touch: swipe shelves, ☆ on each tile, ‹ › arrows for mouse.
  - Storage (all under `game-hub/`, backed up by family-cloud): `settings` {lang, sound}, `recent` {v:1, list:[{id, at}]}, `favs` {v:1, ids}, and `last` {id, at} kept for older hub versions.
  - Tests: `python3 tests/test_hub.py` (Playwright: TV with 1/2/4 mocked controllers, Xbox user agent, iPad touch in both orientations, keyboard, four languages, TV readability, bad data).
- `dragon-gems/`, `crab-castle/`: copied unchanged from their claude.ai artifacts on 2026-11-13. Only each launcher `index.html` gained one line that loads `shared/family-cloud.js`.
- `community/`: 社区游戏 · community games — open-source games other people made with AI (Claude, Grok…), each with its licence and credit. They run sandboxed through `community/play.html`, so they can't touch the family games' data. See `community/README.md`.
- `tests/`: Playwright tests for the hub (`test_hub.py`) and the community games (`test_community.py`).
- `shared/family-cloud.js`: automatic cloud backup for every localStorage game (one Google sign-in per device covers all games, because they share this origin). Load it with `data-games` (list of game ids) and `data-chip` (`hub`, `float` or `none`).
- `goat-mayhem/`: Goat Mayhem (3D goat sandbox; v1 uses `vendor/three-0.160.min.js`, v2+ use `vendor/three-0.160.module.min.js` with `vendor/three-addons-0.160/`, the KayKit CC0 mannequin and animations in `vendor/kaykit/` and Quaternius CC0 farm animals in `vendor/quaternius/`; v6+ load PeerJS 1.5.5 (MIT) from `vendor/peerjs-1.5.5.min.js` for online play). Launcher `index.html`, `versions.json`, frozen `goat-mayhem-vN.html`, `CHANGELOG.md`, sample save `fixture-s1.json`.
- `drawrassic-park/`: Drawrassic Park. `index.html` is the version launcher, `versions.json` lists the versions, each version is `drawrassic-park-vN.html` (old versions are frozen), and `CHANGELOG.md` is the changelog.
- `vendor/firebase-lite.js`: Firebase JS SDK 13.3.0 (app, auth, firestore), bundled with esbuild, so the games don't depend on a CDN.

## Cloud backup (Firebase project `family-games-f885f`)
- Google sign-in. Firestore data lives under `users/{uid}/...`.
- `firestore.rules` is the template for the security rules. The live rules in the Firebase console also restrict access to the family's Google account(s). That list is not stored here, because this repository is public.

## Data safety
See the "Never lose player data" rules in the Claude project (`family-game-studio/data-safety-rules.md`).
