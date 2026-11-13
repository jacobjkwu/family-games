# 社区游戏 · Community games

Open-source games that other people made with AI models, copied here so they play inside the Game Hub.
Each game keeps its own licence file (all MIT) and is credited on its hub card and in the bar above the game.

## How they run
- The hub opens `community/play.html?g=<id>`. That page shows a bar (← Game Hub, credit + source link, ☁️, Fullscreen)
  and runs the game in a **sandboxed iframe without `allow-same-origin`**. The game gets an opaque origin, so it can't
  read or change the family games' saves, settings, cookies or the cloud sign-in on this website, and it can't
  navigate the hub page.
- `shim.js` is the first script of every game page. It gives the game an in-memory `localStorage`/`sessionStorage`
  that play.html saves under `community/<id>/save` (with `/bak`, 7 daily `/bak-dYYYYMMDD` copies, and
  `/broken-<time>` for unreadable data). If a game page is opened directly, the shim stops it before any game
  script runs and redirects to play.html.
- Cloud backup: each game is listed in `shared/family-cloud.js` as `community-<id>`; play.html loads it, and the ☁️ button opens the cloud menu.
- Controller: hold **B** for 1.5 s to go back to the hub. Gameplay itself is touch/mouse/keyboard, as each game was made.
- GitHub Pages sends `Access-Control-Allow-Origin: *`, which the sandboxed games need to load their module scripts and files.

## Games

| id | Game | Author | Made with | Source (commit copied) | Changes made here |
|---|---|---|---|---|---|
| bloom-hop | Bloom Hop | zeveck | Claude Code (art/sound from AI image/audio tools) | [zeveck/bloom-hop](https://github.com/zeveck/bloom-hop) `c5e7548` | `game/` copied without sw.js/SEO files; shim tag |
| puffling-flight | Puffling Flight · 小海鹦飞飞 | connect-world-1985-ai | Claude (plan and game code) + Grok (build) | [connect-world-1985-ai/2026-10-26-puffling-flight-plan-claude-build-grok](https://github.com/connect-world-1985-ai/2026-10-26-puffling-flight-plan-claude-build-grok) `905137d` | only `play/` (the game); shim tag |
| pixel-princess | Pixel Princess Platformer | Vito D'Elia | Claude Code | [VTvito/pixel-princess-platformer](https://github.com/VTvito/pixel-princess-platformer) `ba20bc4` | runtime files only (no api/, tools/, sw.js); shim tag. The online leaderboard shows "unavailable". |
| casa-de-gemas | Casa de Gemas | deepujain | Claude Opus 5.5 (in Cursor) | [deepujain/casadegema](https://github.com/deepujain/casadegema) `e1545d2` | the tap-only `mobile/index.html` as index.html; shim tag |
| magic-puzzle | Maher Magic Sliding Puzzle | Maher Khan | Claude Code | [maherkhan-builds/maher-magic-puzzle](https://github.com/maherkhan-builds/maher-magic-puzzle) `3dd6e4a` | shim tag |
| sudoku | Sudoku | AI Index team (miscusi-crew) | Claude Code | [miscusi-crew/aiindex-sudoku](https://github.com/miscusi-crew/aiindex-sudoku) `74686de` | `app/` copied; shim tag |
| kapadokya-balonu | Kapadokya Balonu | Furkiozknn | Claude Opus 5.5 | [Furkiozknn/kapadokya-balonu](https://github.com/Furkiozknn/kapadokya-balonu) `7579422` | three.js 0.170.0 served locally instead of jsDelivr; GoatCounter analytics removed; shim tag |
| karagoz | Karagöz | Furkiozknn | Claude Opus 5.5 | [Furkiozknn/karagoz](https://github.com/Furkiozknn/karagoz) `1f62cbf` | same as Kapadokya Balonu |

Vendored three.js keeps its own MIT licence in `vendor/three/LICENSE`.

## Adding a community game
1. Only games with an open-source licence that allows copying (MIT, Apache-2.0, BSD, CC0…), that run as static
   files with no build step and no server, and that suit the family.
2. `python3 tools/vendor_community.py <clone> <id> <entry.html> <files…>` copies it and adds the shim tag.
3. Add an entry to `games.json` with `"category": "community"`, `url`, `entry`, `credit`, names/blurbs in four languages and a hand-drawn icon,
   and a `community-<id>` line to the GAMES table in `shared/family-cloud.js`.
4. Run `python3 tests/test_community.py` and `python3 tests/test_hub.py`.
