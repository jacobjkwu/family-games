# Family Games

Games built with Claude, hosted on GitHub Pages: https://jacobjkwu.github.io/family-games/

- `drawrassic-park/`: Drawrassic Park. `index.html` is the version launcher, `versions.json` lists the versions, each version is `drawrassic-park-vN.html` (old versions are frozen), and `CHANGELOG.md` is the changelog.
- `vendor/firebase-lite.js`: Firebase JS SDK 13.3.0 (app, auth, firestore), bundled with esbuild, so the games don't depend on a CDN.

## Cloud backup (Firebase project `family-games-f885f`)
- Google sign-in. Firestore data lives under `users/{uid}/...`.
- `firestore.rules` is the template for the security rules. The live rules in the Firebase console also restrict access to the family's Google account(s). That list is not stored here, because this repository is public.

## Data safety
See the "Never lose player data" rules in the Claude project (`family-game-studio/data-safety-rules.md`).
