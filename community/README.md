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

## Three ways a community game is in the hub
- **copied** (`entry`): the files are in `community/<id>/` (open-source licence that allows copying, static files). Runs sandboxed through `play.html`, saves under `community/<id>/save`, cloud-backed.
- **embedded** (`external`): `play.html` shows the game's own official website in the frame. Used for games without a licence (we may not copy them), games that need a build step, and closed-source games. Their saves stay on their own website (in Safari, separately from visiting that site directly) and are not in our cloud backup. If a site ever refuses to be shown in a frame, the **↗** button in the bar opens it in a new tab.
- **link** (`link: true`): the card opens the site directly (claude.ai artifacts, patch.gg and remix.gg pages, which don't run inside other pages). Use the browser's back button to return.

Not included on purpose: shooters, horror and gore, gambling, chat with strangers, and look-alikes of other companies' characters (two "Mario Kart" clones were removed for that reason).

## Games

| id | Game | Author | Made with | How | Input | Source / site |
|---|---|---|---|---|---|---|
| bloom-hop | Bloom Hop | zeveck | Claude Code | copied | 👆 touch | https://github.com/zeveck/bloom-hop |
| puffling-flight | Puffling Flight | connect-world-1985-ai | Claude + Grok | copied | 👆 touch | https://github.com/connect-world-1985-ai/2026-10-26-puffling-flight-plan-claude-build-grok |
| pixel-princess | Pixel Princess Platformer | Vito D'Elia | Claude Code | copied | 👆 touch | https://github.com/VTvito/pixel-princess-platformer |
| casa-de-gemas | Casa de Gemas | deepujain | Claude Opus 5.5 | copied | 👆 touch | https://github.com/deepujain/casadegema |
| magic-puzzle | Magic Sliding Puzzle | Maher Khan | Claude Code | copied | 👆 touch | https://github.com/maherkhan-builds/maher-magic-puzzle |
| sudoku | Sudoku | AI Index (miscusi-crew) | Claude Code | copied | 👆 touch | https://github.com/miscusi-crew/aiindex-sudoku |
| kapadokya-balonu | Cappadocia Balloon | Furkiozknn | Claude Opus 5.5 | copied | 👆 touch | https://github.com/Furkiozknn/kapadokya-balonu |
| karagoz | Karagöz Shadow Theatre | Furkiozknn | Claude Opus 5.5 | copied | 👆 touch | https://github.com/Furkiozknn/karagoz |
| kindle | KINDLE | Tony Downey | Claude Opus 5 | copied | 👆 touch | https://github.com/TonyDowney/kindle |
| hoard-hopper | Hoard Hopper | zeveck | Claude Opus 5.5 | copied | 👆 touch | https://github.com/zeveck/hoardhopper |
| cozy-bakery | Cozy Bakery | goncalo_canhoto | Claude Fable 5.2 | embedded | 👆🎮 touch or controller | https://cozybakery.vercel.app/ |
| cozy-lisbon | Cozy Lisbon | goncalo_canhoto | Claude Fable 5.2 | embedded | 👆 touch | https://cozylisbon.vercel.app/ |
| yardclash | YARDCLASH | AugustCastilIo | Claude Fable 5.2 | embedded | 👆 touch | https://yardclash.vercel.app/ |
| giant-leap | Giant Leap | handsher_NGU | Claude Fable 5.2 | embedded | 👆 touch | https://giant-leap.vercel.app/ |
| tilt-labyrinth | Tilt Labyrinth | mylifcc | Claude Fable 5.2 | embedded | 👆 touch | https://blog.silencestar.com/posts/tilt-labyrinth/play/ |
| tree-appreciator | Tree Appreciator | Simon Willison | Claude Opus 5.5 | embedded | 👆 touch | https://tools.simonwillison.net/tree-appreciator |
| yarn-planet | Yarn Planet | Maker Jackie | Claude Opus 5.5 | embedded | 👆 touch | https://github.com/makerjackie/yarn-planet |
| little-flock | Little Flock | songkeys | GPT-6 Astra (Codex) | embedded | 👆 touch | https://github.com/songkeys/little-flock |
| driftwing | DRIFTWING | KyleBuildsAI | Claude Opus 5.5 | embedded | 👆🎮 touch or controller | https://kylebuildsai.github.io/driftwing/ |
| fall-line | Fall Line | Nipale-ai | Claude Opus 5.5 | embedded | 👆🎮 touch or controller | https://nipale-ai.github.io/opus-5-5-overnight-builds/fall-line/ |
| palmera-bay | Palmera Bay | vcahlik | Claude Opus 5.5 | embedded | 👆🎮 touch or controller | https://cahlik.net/palmera-bay/ |
| three-cats | Moe, Joe & Mr Mews | lambsubstitute | Claude Opus 5.5 | embedded | 👆 touch | https://lambsubstitute.github.io/three-cats/ |
| fishslop | Fishslop | vasu-devs | Claude Opus 5.5 | embedded | 👆 touch | https://vasu-devs.github.io/FishSlop_Opus5.5/ |
| solitaire | Solitaire | venkatarangan | GPT-6 Astra | embedded | 👆 touch | https://solitaire.mangoidiots.com/ |
| bubble-wrap | Bubble Wrap Simulator | finktheartist | GPT-6 Astra | embedded | 👆 touch | https://bubble-wrap-simulator.vercel.app/ |
| rift-chess | Rift Chess | HaileyStorm | GPT-6 Astra | embedded | 👆 touch | https://github.com/HaileyStorm/rift-chess |
| thunder-valley | Thunder Valley | loktar00 | Claude Fable 5.2 | embedded | 👆 touch | https://loktar00.github.io/llm-test-pages/fable52-dino-chase/ |
| lanternfall | LANTERNFALL | loktar00 | Claude Fable 5.2 | embedded | 👆 touch | https://loktar00.github.io/lanternfall/ |
| opus-100 | 121 Opus projects | swan4er | Claude Opus 5.5 | embedded | 👆 touch | https://swan4er.github.io/opus-100-projects/ |
| cayley | Cayley flight simulator | lionel_mora | Claude Fable 5.2 | embedded | 🎮 controller/keyboard | https://github.com/lauramionel/cayley-flight-simulator |
| starry-nightrider | Starry Nightrider | ebbyamir | Claude Fable 5.2 | embedded | ⌨️ keyboard & mouse | https://starrynightrider.com/ |
| what-the-water-keeps | What the Water Keeps | kevin_t_ngo | Claude Fable 5.2 | embedded | ⌨️ keyboard & mouse | https://what-the-water-keeps.vercel.app/ |
| waking-river | The Waking River | flxrnc | Claude Fable 5.2 | embedded | ⌨️ keyboard & mouse | https://rivergame-kappa.vercel.app/ |
| turbo-tails | Turbo Tails | petergyang | Claude Fable 5.2 | embedded | ⌨️ keyboard & mouse | https://turbo-tails.vercel.app/ |
| capybara-delivery | A Game About Capybaras Delivering Food | leocoout | Claude Code | embedded | ⌨️ keyboard & mouse | https://capybara-vibejam26.leocoout.dev/ |
| bwca-canoe | BWCA Canoe | Gkrumbach07 | Claude Opus 5.5 | embedded | ⌨️ keyboard & mouse | https://gkrumbach07.github.io/bwca-canoe/ |
| oil-paint | Oil Paint | BlendiByl | Claude Fable 5.2 | link | 🎮 controller/keyboard | https://patch.gg/blendi/oil-paint |
| patchwork-quilt | Patchwork Quilt | BlendiByl | Claude Fable 5.2 | link | ⌨️ keyboard & mouse | https://patch.gg/blendi/patchwork-quilt |
| banana-mine-rush | Banana Mine Rush | 0xChuckstock | Claude Fable 5.2 | link | 👆 touch | https://remix.gg/g/banana-mine-rush |
| hoppy-meadow | Hoppy Meadow | 0xChuckstock | Claude Fable 5.2 | link | 👆 touch | https://remix.gg/g/hoppy-meadow |
| brix-84 | BRIX ’84 | 0xChuckstock | Claude Fable 5.2 | link | 👆 touch | https://remix.gg/g/brix-84 |
| stray-cat | Stray Cat | aimikoda | Claude Fable 5.2 | link | ⌨️ keyboard & mouse | https://claude.ai/artifact/4nPXUKJjQWNsZEHVNmXXCt |
| midnight-pass | Midnight Pass | andreysuperior | Claude Fable 5.2 | link | ⌨️ keyboard & mouse | https://claude.ai/artifact/UD9pGEN4QFA8F5EadRw8eL |
| roost | Roost | tejas3732 | Claude Fable 5.2 | link | ⌨️ keyboard & mouse | https://claude.ai/artifact/DLnFodkTwvawCNwurDmSZK?sk=5N6PtC07f1niB7h3I6clZQ |
| kart-adventure | Open-world kart adventure | realWeZZard | Claude Fable 5.2 | link | ⌨️ keyboard & mouse | https://claude.ai/artifact/FpdQ81sJs1KiV1a6JCY4jj |

Copied games: changes made here are only the shim tag (all), three.js 0.170.0 served locally and GoatCounter removed (Kapadokya Balonu, Karagöz), Casa de Gemas uses its tap-only `mobile/` page.
Commits copied: bloom-hop `c5e7548`, puffling-flight `905137d`, pixel-princess `ba20bc4`, casa-de-gemas `e1545d2`, magic-puzzle `3dd6e4a`, sudoku `74686de`, kapadokya-balonu `7579422`, karagoz `1f62cbf`, kindle `dfe9240`, hoard-hopper `539196d`.

## Adding a community game
1. Kid-appropriate, made mostly by an AI model, plays in a browser. Copy it only with a licence that allows it and no build step;
   otherwise embed its official https site (or link it if the site won't run in a frame).
2. Copy: `python3 tools/vendor_community.py <clone> <id> <entry.html> <files…> [--three]`, then add `"entry"` in games.json and a `community-<id>` line to the GAMES table in `shared/family-cloud.js`.
   Embed: add `"external": "https://…"`. Link: `"url": "https://…", "link": true`.
3. Every entry: `"category": "community"`, `input` (touch | both | controller | keyboard), names/blurbs in four languages, `credit`, icon.
4. Run `python3 tests/test_community.py` and `python3 tests/test_hub.py`.
