/* family-cloud.js — automatic cloud backup for every family game on this website.
   All games on one address share one origin and localStorage (GitHub Pages and Vercel are separate origins).
   This module backs up each game's keys to Firestore (users/{uid}/ls/{game}),
   keeps hourly/daily history, offers newer progress from other devices, and
   restores a game after backing up the local copy.
   Use: <script type="module" src="…/shared/family-cloud.js" data-games="dragon-gems,crab-castle" data-chip="hub|float|none"></script>
   Drawrassic Park is not listed here: it has its own cloud backup inside the game (v3.5+).
   Friends (2026-11-13): a Google account that is neither family nor approved can ask to join (requests/{uid});
   the family approves in the hub (☁️ → 👪), which writes allowed/{email}. The hub chip shows 🔔 when someone waits,
   and an email goes to the family through EmailJS (public ids only; the address lives in the EmailJS template).
   Rules: firestore.rules (template; the family email is only in the live rules in the Firebase console). */
const ME = document.currentScript || document.querySelector('script[src*="family-cloud.js"]');
const FIREBASE_CONFIG = { apiKey: "AIzaSyAwntOUxxrUjgz1aaHRMrCtxw_FxF2mFC4", authDomain: "family-games-f885f.firebaseapp.com", projectId: "family-games-f885f",
  storageBucket: "family-games-f885f.firebasestorage.app", messagingSenderId: "764444204536", appId: "1:764444204536:web:ab9aa90cfda700130b8a0d" };
const CFG = { checkEveryMs: 60000, keepHourly: 48, keepDaily: 30, maxChars: 900000, deadZone: 0.15 };
const GAMES = {
  'dragon-gems': { prefixes: ['dragon-gems/'], exact: ['dragonGemMountain.v1'], name: { en: "Dragon's Gem Mountain", fr: 'La Montagne aux Gemmes', 'zh-Hans': '喷火龙的宝石山', 'zh-Hant': '噴火龍的寶石山' } },
  'crab-castle': { prefixes: ['crab-castle/'], exact: ['crab3d'], name: { en: 'Crab King Castle Defense', fr: 'Le Roi Crabe défend son château', 'zh-Hans': '巨蟹王城堡保卫战', 'zh-Hant': '巨蟹王城堡保衛戰' } },
  'goat-mayhem': { prefixes: ['goat-mayhem/'], exact: [], name: { en: 'Goat Mayhem', fr: 'Chèvre en Folie', 'zh-Hans': '疯狂山羊', 'zh-Hant': '瘋狂山羊' } },
  'game-hub': { prefixes: ['game-hub/'], exact: [], name: { en: 'Game Hub settings', fr: 'Réglages de la salle de jeux', 'zh-Hans': '游戏大厅设置', 'zh-Hant': '遊戲大廳設定' } },
  // community games (community/play.html): each one saves under community/<id>/
  'community-bloom-hop': { prefixes: ['community/bloom-hop/'], exact: [], name: {"en": "🌐 Bloom Hop", "fr": "🌐 Bloom Hop", "zh-Hans": "🌐 荷塘跳跳蛙 Bloom Hop", "zh-Hant": "🌐 荷塘跳跳蛙 Bloom Hop"} },
  'community-puffling-flight': { prefixes: ['community/puffling-flight/'], exact: [], name: {"en": "🌐 Puffling Flight", "fr": "🌐 Le vol du macareux", "zh-Hans": "🌐 小海鹦飞飞", "zh-Hant": "🌐 小海鸚飛飛"} },
  'community-pixel-princess': { prefixes: ['community/pixel-princess/'], exact: [], name: {"en": "🌐 Pixel Princess Platformer", "fr": "🌐 Pixel Princess Platformer", "zh-Hans": "🌐 像素公主闯关", "zh-Hant": "🌐 像素公主闖關"} },
  'community-casa-de-gemas': { prefixes: ['community/casa-de-gemas/'], exact: [], name: {"en": "🌐 Casa de Gemas", "fr": "🌐 Casa de Gemas", "zh-Hans": "🌐 宝石小屋", "zh-Hant": "🌐 寶石小屋"} },
  'community-magic-puzzle': { prefixes: ['community/magic-puzzle/'], exact: [], name: {"en": "🌐 Magic Sliding Puzzle", "fr": "🌐 Taquin magique", "zh-Hans": "🌐 魔法滑块拼图", "zh-Hant": "🌐 魔法滑塊拼圖"} },
  'community-sudoku': { prefixes: ['community/sudoku/'], exact: [], name: {"en": "🌐 Sudoku", "fr": "🌐 Sudoku", "zh-Hans": "🌐 数独", "zh-Hant": "🌐 數獨"} },
  'community-kapadokya-balonu': { prefixes: ['community/kapadokya-balonu/'], exact: [], name: {"en": "🌐 Cappadocia Balloon", "fr": "🌐 Montgolfière de Cappadoce", "zh-Hans": "🌐 卡帕多奇亚热气球", "zh-Hant": "🌐 卡帕多奇亞熱氣球"} },
  'community-karagoz': { prefixes: ['community/karagoz/'], exact: [], name: {"en": "🌐 Karagöz Shadow Theatre", "fr": "🌐 Théâtre d’ombres Karagöz", "zh-Hans": "🌐 皮影戏光影谜题", "zh-Hant": "🌐 皮影戲光影謎題"} },
  'community-kindle': { prefixes: ['community/kindle/'], exact: [], name: {"en": "🌐 KINDLE", "fr": "🌐 KINDLE", "zh-Hans": "🌐 点灯人 KINDLE", "zh-Hant": "🌐 點燈人 KINDLE"} },
  'community-hoard-hopper': { prefixes: ['community/hoard-hopper/'], exact: [], name: {"en": "🌐 Hoard Hopper", "fr": "🌐 Hoard Hopper", "zh-Hans": "🌐 小龙宝藏跳跳", "zh-Hant": "🌐 小龍寶藏跳跳"} },
};
const STATE_KEY = 'family-cloud/state';
// EmailJS: these three ids are public by design (they are sent from every browser); the family's address is in the template on emailjs.com.
const MAIL = { url: 'https://api.emailjs.com/api/v1.0/email/send', service: 'service_bek97rc', template: 'template_pc1o6xn', key: 'svOtj7oJPatD7u-rV', hub: new URL('../', import.meta.url).href };   // the hub on whichever address this page came from (GitHub Pages or Vercel)
const STR = {
  en: { friendsBtn: '👪 Friends waiting ({n})', friendsNone: 'No one is waiting.', friendsT: '👪 Friends who want to join', reqLine: '{name}\n{email} · asked {t}', approve: '✅ Approve', deny: '❌ Not approved', later: 'Later',
    approved: '✅ {name} can now use the family cloud.', denied: '{name} was not approved.', membersBtn: '👥 Approved friends', membersNone: 'No approved friends yet.', removeT: 'Remove this friend?', removeB: '{name} ({email}) will no longer be able to use the family cloud. Their saves in the cloud are kept.', remove: '🗑️ Remove', removed: '{name} was removed.',
    applyT: '👋 Ask to join the family cloud', applyB: 'You are signed in as {e}.\nThis cloud is only for the family and friends they approve. Write your name and send a request; a grown-up of the family will check it.', namePh: 'Your name', send: '📨 Send request', nameNeed: 'Please write your name first.', sent: '📨 Request sent! A grown-up will check it soon.',
    pendingB: 'Signed in as {e}.\n⏳ Waiting for a grown-up of the family to approve you (asked {t}).', deniedB: 'Signed in as {e}.\nYour request to join the family cloud was not approved.', cancelReq: 'Cancel my request', welcome: '🎉 You are approved! Cloud backup is on.', newReq: '🔔 {n} friend(s) want to join the family cloud. Open ☁️ to check.', guestChip: '☁️ Ask to join', pendingChip: '☁️ ⏳ Waiting for approval',
    chipReady: '☁️ Cloud backup on', pairStart: '📺 Use a pairing code (no typing here)', pairT: '📺 Pairing code', pairB: 'On an iPad or computer that is signed in: open the Game Hub → ☁️ → “📺 Pair another device”, and type this code:', pairWait: 'Waiting for the other device…', pairOk: '📺 Paired with {e}’s cloud saves.', pairOld: 'This code has expired. Start again.', pairOther: '📺 Pair another device', pairEnter: 'Type the 6-letter code shown on the TV:', pairBad: 'No device is waiting with that code. Check the code on the TV.', pairDone: '📺 Device paired. It now uses your cloud saves.', ok: 'OK', pairedAs: 'Paired with {e}’s cloud saves', unpair: 'Unpair this device', cancel: 'Cancel', chipOff: '☁️ Turn on cloud backup', chipOn: '☁️ Backed up {t}', chipBusy: '☁️ Backing up…', chipErr: '☁️ Backup problem', title: '☁️ Cloud backup',
    homeB: 'This is a Home Screen app, and iPad doesn’t let the Google sign-in window send its answer back here. Use a pairing code instead: tap “📺 Use a pairing code” below, then open this site in Safari, sign in with Google there (Game Hub → ☁️), choose “📺 Pair another device” and type the code.', signedOut: 'Sign in with Google once on this device, and every game backs itself up to the cloud.', signIn: 'Sign in with Google', signOut: 'Sign out',
    as: 'Signed in as {e}', upAll: '⬆️ Back up now', restore: '⬇️ Restore a game…', close: 'Close', pickGame: 'Which game?', pickSnap: 'Which backup?', none: 'No cloud backups yet.',
    newerT: '☁️ Newer progress in the cloud', newerB: '{g}: progress from {d}, {t}.\nLoad it on this device? This device’s progress is kept as a backup first.', load: 'Load it', keep: 'Keep this device’s',
    loadOk: '☁️ {g}: cloud progress loaded.', upOk: '☁️ All games backed up.', err: 'Cloud backup problem: {m}', confirmT: 'Restore this backup?', confirmB: '{g}: backup from {d}, {t}.\nThis device’s progress is kept as a backup first.',
    never: 'never', justNow: 'just now', ago: '{t} ago', min: '{n} min', hr: '{n} h', day: '{n} days', lastUp: '{g}: last backup {t}', drawrassic: 'Drawrassic Park backs itself up inside the game (⚙️ settings).',
    dev: { ipad: 'iPad', iphone: 'iPhone', xbox: 'Xbox', pc: 'PC', mac: 'Mac', android: 'Android', other: 'another device' } },
  fr: { friendsBtn: '👪 Amis en attente ({n})', friendsNone: 'Personne n’attend.', friendsT: '👪 Amis qui veulent entrer', reqLine: '{name}\n{email} · demandé {t}', approve: '✅ Accepter', deny: '❌ Refuser', later: 'Plus tard',
    approved: '✅ {name} peut maintenant utiliser le cloud de la famille.', denied: '{name} n’a pas été accepté.', membersBtn: '👥 Amis acceptés', membersNone: 'Pas encore d’amis acceptés.', removeT: 'Retirer cet ami ?', removeB: '{name} ({email}) ne pourra plus utiliser le cloud de la famille. Ses sauvegardes dans le cloud sont gardées.', remove: '🗑️ Retirer', removed: '{name} a été retiré.',
    applyT: '👋 Demander à rejoindre le cloud de la famille', applyB: 'Tu es connecté : {e}.\nCe cloud est réservé à la famille et aux amis qu’elle accepte. Écris ton nom et envoie une demande ; un adulte de la famille la vérifiera.', namePh: 'Ton nom', send: '📨 Envoyer la demande', nameNeed: 'Écris d’abord ton nom.', sent: '📨 Demande envoyée ! Un adulte va la vérifier bientôt.',
    pendingB: 'Connecté : {e}.\n⏳ En attente de l’accord d’un adulte de la famille (demandé {t}).', deniedB: 'Connecté : {e}.\nTa demande pour rejoindre le cloud de la famille n’a pas été acceptée.', cancelReq: 'Annuler ma demande', welcome: '🎉 Tu es accepté ! La sauvegarde cloud est activée.', newReq: '🔔 {n} ami(s) veulent rejoindre le cloud de la famille. Ouvre ☁️ pour voir.', guestChip: '☁️ Demander à rejoindre', pendingChip: '☁️ ⏳ En attente d’accord',
    chipReady: '☁️ Sauvegarde cloud activée', pairStart: '📺 Utiliser un code d’appairage (rien à taper ici)', pairT: '📺 Code d’appairage', pairB: 'Sur un iPad ou un ordinateur connecté : ouvre la salle de jeux → ☁️ → « 📺 Appairer un autre appareil », puis tape ce code :', pairWait: 'En attente de l’autre appareil…', pairOk: '📺 Appairé aux sauvegardes de {e}.', pairOld: 'Ce code a expiré. Recommence.', pairOther: '📺 Appairer un autre appareil', pairEnter: 'Tape le code de 6 lettres affiché sur la télé :', pairBad: 'Aucun appareil n’attend avec ce code. Vérifie le code sur la télé.', pairDone: '📺 Appareil appairé. Il utilise maintenant tes sauvegardes cloud.', ok: 'OK', pairedAs: 'Appairé aux sauvegardes de {e}', unpair: 'Désappairer cet appareil', cancel: 'Annuler', chipOff: '☁️ Activer la sauvegarde cloud', chipOn: '☁️ Sauvegardé {t}', chipBusy: '☁️ Sauvegarde…', chipErr: '☁️ Problème de sauvegarde', title: '☁️ Sauvegarde cloud',
    homeB: 'C’est une app de l’écran d’accueil : l’iPad ne laisse pas la fenêtre de connexion Google renvoyer la réponse ici. Utilise plutôt un code d’appairage : touche « 📺 Utiliser un code d’appairage » ci-dessous, puis ouvre ce site dans Safari, connecte-toi avec Google (salle de jeux → ☁️), choisis « 📺 Appairer un autre appareil » et tape le code.', signedOut: 'Connecte-toi une fois avec Google sur cet appareil, et chaque jeu se sauvegarde tout seul dans le cloud.', signIn: 'Se connecter avec Google', signOut: 'Se déconnecter',
    as: 'Connecté : {e}', upAll: '⬆️ Sauvegarder maintenant', restore: '⬇️ Restaurer un jeu…', close: 'Fermer', pickGame: 'Quel jeu ?', pickSnap: 'Quelle sauvegarde ?', none: 'Pas encore de sauvegarde dans le cloud.',
    newerT: '☁️ Progression plus récente dans le cloud', newerB: '{g} : progression de {d}, {t}.\nLa charger sur cet appareil ? La progression de cet appareil est d’abord gardée en copie.', load: 'La charger', keep: 'Garder celle-ci',
    loadOk: '☁️ {g} : progression du cloud chargée.', upOk: '☁️ Tous les jeux sont sauvegardés.', err: 'Problème de sauvegarde cloud : {m}', confirmT: 'Restaurer cette sauvegarde ?', confirmB: '{g} : sauvegarde de {d}, {t}.\nLa progression de cet appareil est d’abord gardée en copie.',
    never: 'jamais', justNow: 'à l’instant', ago: 'il y a {t}', min: '{n} min', hr: '{n} h', day: '{n} jours', lastUp: '{g} : dernière sauvegarde {t}', drawrassic: 'Drawrassic Park se sauvegarde dans le jeu (⚙️ réglages).',
    dev: { ipad: 'iPad', iphone: 'iPhone', xbox: 'Xbox', pc: 'PC', mac: 'Mac', android: 'Android', other: 'un autre appareil' } },
  'zh-Hans': { friendsBtn: '👪 等待批准的朋友（{n}）', friendsNone: '现在没有人在等。', friendsT: '👪 想加入的朋友', reqLine: '{name}\n{email} · {t}申请', approve: '✅ 同意', deny: '❌ 不同意', later: '等会儿再说',
    approved: '✅ {name} 现在可以用家庭云端了。', denied: '没有同意 {name} 的申请。', membersBtn: '👥 已批准的朋友', membersNone: '还没有批准过朋友。', removeT: '移除这个朋友？', removeB: '{name}（{email}）以后不能再用家庭云端了。他在云端的存档会保留。', remove: '🗑️ 移除', removed: '已移除 {name}。',
    applyT: '👋 申请加入家庭云端', applyB: '你已登录：{e}。\n这个云端只给家里人和他们批准的朋友用。写上你的名字，发出申请，家里的大人会来看。', namePh: '你的名字', send: '📨 发送申请', nameNeed: '请先写上你的名字。', sent: '📨 申请已发出！家里的大人很快会看到。',
    pendingB: '已登录：{e}。\n⏳ 正在等家里的大人批准（{t}申请的）。', deniedB: '已登录：{e}。\n你加入家庭云端的申请没有被同意。', cancelReq: '取消我的申请', welcome: '🎉 申请通过啦！云备份已开启。', newReq: '🔔 有 {n} 个朋友想加入家庭云端，点 ☁️ 看看。', guestChip: '☁️ 申请加入', pendingChip: '☁️ ⏳ 等待批准',
    chipReady: '☁️ 云备份已开启', pairStart: '📺 用配对码（这里不用打字）', pairT: '📺 配对码', pairB: '在已经登录的 iPad 或电脑上：打开游戏大厅 → ☁️ → “📺 配对另一台设备”，输入这个码：', pairWait: '正在等另一台设备…', pairOk: '📺 已经和 {e} 的云存档配对好了。', pairOld: '这个码过期了，请重新开始。', pairOther: '📺 配对另一台设备', pairEnter: '输入电视上显示的 6 位码：', pairBad: '没有设备在用这个码等待。请核对电视上的码。', pairDone: '📺 配对成功！那台设备现在用你的云存档了。', ok: '确定', pairedAs: '已和 {e} 的云存档配对', unpair: '取消这台设备的配对', cancel: '取消', chipOff: '☁️ 开启云备份', chipOn: '☁️ 已备份 · {t}', chipBusy: '☁️ 正在备份…', chipErr: '☁️ 备份出了问题', title: '☁️ 云备份',
    homeB: '这是主屏幕上的 App。iPad 不让 Google 登录窗口把结果送回这里，所以会登录不了。请改用配对码：点下面的“📺 用配对码”，然后用 Safari 打开这个网站，在那里用 Google 登录（游戏大厅 → ☁️），再点“📺 配对另一台设备”，输入配对码。', signedOut: '在这台设备上用 Google 登录一次，所有游戏都会自动备份到云端。', signIn: '用 Google 登录', signOut: '退出登录',
    as: '已登录：{e}', upAll: '⬆️ 立即备份', restore: '⬇️ 恢复某个游戏…', close: '关闭', pickGame: '恢复哪个游戏？', pickSnap: '用哪一份备份？', none: '云端还没有备份。',
    newerT: '☁️ 云端有更新的进度', newerB: '{g}：来自 {d} 的进度，{t}。\n要载入到这台设备吗？这台设备现在的进度会先留一份备份。', load: '载入', keep: '保留这台的',
    loadOk: '☁️ {g}：云端进度已载入。', upOk: '☁️ 所有游戏都备份好了。', err: '云备份出了问题：{m}', confirmT: '恢复这份备份？', confirmB: '{g}：来自 {d} 的备份，{t}。\n这台设备现在的进度会先留一份备份。',
    never: '还没有', justNow: '刚刚', ago: '{t}前', min: '{n} 分钟', hr: '{n} 小时', day: '{n} 天', lastUp: '{g}：上次备份 {t}', drawrassic: 'Drawrassic Park 在游戏里自己备份（⚙️ 设置）。',
    dev: { ipad: 'iPad', iphone: 'iPhone', xbox: 'Xbox', pc: '电脑', mac: 'Mac', android: '安卓设备', other: '另一台设备' } },
  'zh-Hant': { friendsBtn: '👪 等待批准的朋友（{n}）', friendsNone: '現在沒有人在等。', friendsT: '👪 想加入的朋友', reqLine: '{name}\n{email} · {t}申請', approve: '✅ 同意', deny: '❌ 不同意', later: '等會兒再說',
    approved: '✅ {name} 現在可以用家庭雲端了。', denied: '沒有同意 {name} 的申請。', membersBtn: '👥 已批准的朋友', membersNone: '還沒有批准過朋友。', removeT: '移除這個朋友？', removeB: '{name}（{email}）以後不能再用家庭雲端了。他在雲端的存檔會保留。', remove: '🗑️ 移除', removed: '已移除 {name}。',
    applyT: '👋 申請加入家庭雲端', applyB: '你已登入：{e}。\n這個雲端只給家裡人和他們批准的朋友用。寫上你的名字，送出申請，家裡的大人會來看。', namePh: '你的名字', send: '📨 送出申請', nameNeed: '請先寫上你的名字。', sent: '📨 申請已送出！家裡的大人很快會看到。',
    pendingB: '已登入：{e}。\n⏳ 正在等家裡的大人批准（{t}申請的）。', deniedB: '已登入：{e}。\n你加入家庭雲端的申請沒有被同意。', cancelReq: '取消我的申請', welcome: '🎉 申請通過啦！雲端備份已開啟。', newReq: '🔔 有 {n} 個朋友想加入家庭雲端，點 ☁️ 看看。', guestChip: '☁️ 申請加入', pendingChip: '☁️ ⏳ 等待批准',
    chipReady: '☁️ 雲端備份已開啟', pairStart: '📺 用配對碼（這裡不用打字）', pairT: '📺 配對碼', pairB: '在已經登入的 iPad 或電腦上：打開遊戲大廳 → ☁️ → 「📺 配對另一台裝置」，輸入這個碼：', pairWait: '正在等另一台裝置…', pairOk: '📺 已經和 {e} 的雲端存檔配對好了。', pairOld: '這個碼過期了，請重新開始。', pairOther: '📺 配對另一台裝置', pairEnter: '輸入電視上顯示的 6 位碼：', pairBad: '沒有裝置在用這個碼等待。請核對電視上的碼。', pairDone: '📺 配對成功！那台裝置現在用你的雲端存檔了。', ok: '確定', pairedAs: '已和 {e} 的雲端存檔配對', unpair: '取消這台裝置的配對', cancel: '取消', chipOff: '☁️ 開啟雲端備份', chipOn: '☁️ 已備份 · {t}', chipBusy: '☁️ 正在備份…', chipErr: '☁️ 備份出了問題', title: '☁️ 雲端備份',
    homeB: '這是主畫面上的 App。iPad 不讓 Google 登入視窗把結果送回這裡，所以會登入不了。請改用配對碼：點下面的「📺 用配對碼」，然後用 Safari 打開這個網站，在那裡用 Google 登入（遊戲大廳 → ☁️），再點「📺 配對另一台裝置」，輸入配對碼。', signedOut: '在這台裝置上用 Google 登入一次，所有遊戲都會自動備份到雲端。', signIn: '用 Google 登入', signOut: '登出',
    as: '已登入：{e}', upAll: '⬆️ 立即備份', restore: '⬇️ 恢復某個遊戲…', close: '關閉', pickGame: '恢復哪個遊戲？', pickSnap: '用哪一份備份？', none: '雲端還沒有備份。',
    newerT: '☁️ 雲端有更新的進度', newerB: '{g}：來自 {d} 的進度，{t}。\n要載入到這台裝置嗎？這台裝置現在的進度會先留一份備份。', load: '載入', keep: '保留這台的',
    loadOk: '☁️ {g}：雲端進度已載入。', upOk: '☁️ 所有遊戲都備份好了。', err: '雲端備份出了問題：{m}', confirmT: '恢復這份備份？', confirmB: '{g}：來自 {d} 的備份，{t}。\n這台裝置現在的進度會先留一份備份。',
    never: '還沒有', justNow: '剛剛', ago: '{t}前', min: '{n} 分鐘', hr: '{n} 小時', day: '{n} 天', lastUp: '{g}：上次備份 {t}', drawrassic: 'Drawrassic Park 在遊戲裡自己備份（⚙️ 設定）。',
    dev: { ipad: 'iPad', iphone: 'iPhone', xbox: 'Xbox', pc: '電腦', mac: 'Mac', android: 'Android 裝置', other: '另一台裝置' } } };

/* ---------- helpers ---------- */
const ls = { get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }, set(k, v) { try { localStorage.setItem(k, v); return true; } catch (e) { return false; } },
  del(k) { try { localStorage.removeItem(k); } catch (e) {} }, keys() { try { return Object.keys(localStorage); } catch (e) { return []; } } };
function lang() { let l = null; for (const k of ['game-hub/settings', 'drawrassic-park/settings', 'dragon-gems/settings', 'crab-castle/settings', 'goat-mayhem/settings']) { try { const o = JSON.parse(ls.get(k) || 'null'); if (o && STR[o.lang]) { l = o.lang; break; } } catch (e) {} }
  if (l) return l; const n = navigator.language || 'en'; if (/^zh-(TW|HK|MO)|^zh-Hant/i.test(n)) return 'zh-Hant'; if (/^zh/i.test(n)) return 'zh-Hans'; if (/^fr/i.test(n)) return 'fr'; return 'en'; }
const T = (k, v = {}) => { const L = STR[lang()] || STR.en; return String(L[k] != null ? L[k] : STR.en[k]).replace(/\{(\w+)\}/g, (m, x) => v[x] != null ? v[x] : m); };
const gName = g => (GAMES[g].name[lang()] || GAMES[g].name.en);
function hash(t) { let a = 0x811c9dc5, b = 0x9e3779b9 ^ t.length; for (let i = 0; i < t.length; i++) { const c = t.charCodeAt(i); a = Math.imul(a ^ c, 16777619); b = Math.imul(b ^ c, 2246822507); } return (a >>> 0).toString(36) + (b >>> 0).toString(36) + t.length.toString(36); }
function state() { try { const o = JSON.parse(ls.get(STATE_KEY) || '{}'); return o && typeof o === 'object' ? o : {}; } catch (e) { return {}; } }
function setState(p) { ls.set(STATE_KEY, JSON.stringify(Object.assign(state(), p))); }
function device() { let s = state(); if (!s.dev) { s.dev = Date.now().toString(36) + Math.random().toString(36).slice(2, 8); setState({ dev: s.dev }); } return s.dev; }
function devKind() { const u = navigator.userAgent || ''; if (/Xbox/i.test(u)) return 'xbox'; if (/iPad/.test(u) || (/Macintosh/.test(u) && navigator.maxTouchPoints > 1)) return 'ipad'; if (/iPhone/.test(u)) return 'iphone';
  if (/Android/i.test(u)) return 'android'; if (/Windows/.test(u)) return 'pc'; if (/Macintosh/.test(u)) return 'mac'; return 'other'; }
const devName = k => { const L = STR[lang()] || STR.en; return L.dev[k] || L.dev.other; };
function ago(at) { if (!at) return T('never'); const m = Math.round((Date.now() - at) / 60000); if (m < 1) return T('justNow'); return T('ago', { t: m < 60 ? T('min', { n: m }) : m < 1440 ? T('hr', { n: Math.round(m / 60) }) : T('day', { n: Math.round(m / 1440) }) }); }
const pad2 = n => String(n).padStart(2, '0');
function ids(at) { const d = new Date(at), day = d.getFullYear() + pad2(d.getMonth() + 1) + pad2(d.getDate()); return { hour: 'h-' + day + '-' + pad2(d.getHours()), day: 'd-' + day }; }
const own = (g, k) => GAMES[g].exact.includes(k) || GAMES[g].prefixes.some(p => k.startsWith(p));
function localData(g) { const o = {}; for (const k of ls.keys().sort()) if (own(g, k) && !/\/(bak|broken-|copy-backup-)/.test(k.slice(k.indexOf('/') + 1)) ) o[k] = ls.get(k); return o; }
function hasProgress(g, data) { return Object.keys(data).some(k => g === 'game-hub' ? true : /save|v1$|crab3d/.test(k)); }

/* ---------- cloud ---------- */
const C = { api: null, user: null, busy: false, err: '', games: [], chip: 'none', role: null, reqs: [], myReq: null, ask: false };
async function loadApi() {
  if (window.__CLOUD_MOCK) return window.__CLOUD_MOCK;
  const fb = await import(new URL('../vendor/firebase-lite.js', import.meta.url).href);
  const app = fb.initializeApp(FIREBASE_CONFIG), auth = fb.getAuth(app), db = fb.getFirestore(app);
  try { await fb.getRedirectResult(auth); } catch (e) {}
  return {
    onUser(cb) { fb.onAuthStateChanged(auth, u => cb(u ? { uid: u.uid, email: u.email || '', anon: !!u.isAnonymous } : null)); },
    signInAnon() { return fb.signInAnonymously(auth); },
    signIn() { const p = new fb.GoogleAuthProvider(); p.setCustomParameters({ prompt: 'select_account' });
      return fb.signInWithPopup(auth, p).catch(e => { const c = (e && e.code) || ''; if (/popup-blocked|operation-not-supported|web-storage-unsupported/.test(c)) return fb.signInWithRedirect(auth, p); throw e; }); },
    signOut() { return fb.signOut(auth); },
    async get(p) { const s = await fb.getDoc(fb.doc(db, p)); return s.exists() ? s.data() : null; },
    set(p, d) { return fb.setDoc(fb.doc(db, p), d); },
    async list(c, n) { const s = await fb.getDocs(fb.query(fb.collection(db, c), fb.orderBy('at', 'desc'), fb.limit(n))); return s.docs.map(x => Object.assign({ id: x.id }, x.data())); },
    del(p) { return fb.deleteDoc(fb.doc(db, p)); },
    mail(body) { return fetch(MAIL.url, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }); } };
}
const ownerUid = () => C.user ? (C.user.anon ? (state().owner || null) : C.user.uid) : null;
const active = () => !!ownerUid() && C.role !== 'guest';   // family, an approved friend, or a paired device
const base = g => 'users/' + ownerUid() + '/ls/' + g;
async function upload(g, force) {
  const data = localData(g); if (!Object.keys(data).length || !hasProgress(g, data)) return false;
  const json = JSON.stringify(data), h = hash(json), st = state(); st.hash = st.hash || {};
  if (!force && st.hash[g] === h) return false;
  if (json.length > CFG.maxChars) throw new Error(gName(g) + ': too big');
  const now = Date.now(), id = ids(now), doc = { at: now, dev: device(), kind: devKind(), hash: h, data: json };
  await C.api.set(base(g) + '/snaps/' + id.hour, doc);
  st.day = st.day || {}; if (st.day[g] !== id.day) { await C.api.set(base(g) + '/snaps/' + id.day, doc); st.day[g] = id.day; prune(g); }
  await C.api.set(base(g), { at: now, dev: doc.dev, kind: doc.kind, hash: h, latest: id.hour });
  st.hash[g] = h; st.up = st.up || {}; st.up[g] = now; st.seen = st.seen || {}; st.seen[g] = now; setState(st); return true;
}
async function prune(g) { try { const list = await C.api.list(base(g) + '/snaps', 200); const hs = list.filter(x => x.id.startsWith('h-')), ds = list.filter(x => x.id.startsWith('d-'));
  for (const x of [...hs.slice(CFG.keepHourly), ...ds.slice(CFG.keepDaily)]) await C.api.del(base(g) + '/snaps/' + x.id); } catch (e) {} }
async function uploadAll(force) { if (!active() || C.busy) return; C.busy = true; C.err = ''; chip();
  let any = false; try { for (const g of C.games) any = (await upload(g, force)) || any; } catch (e) { C.err = (e && (e.code || e.message)) || '?'; }
  C.busy = false; chip(); return any; }
function restoreLocal(g, json) { const data = JSON.parse(json); const cur = localData(g);
  ls.set('family-cloud/bak/' + g, JSON.stringify({ at: Date.now(), data: cur }));
  for (const k of Object.keys(cur)) if (!(k in data)) ls.del(k);
  for (const [k, v] of Object.entries(data)) if (typeof v === 'string') ls.set(k, v);
  const st = state(); st.hash = st.hash || {}; st.hash[g] = hash(JSON.stringify(localData(g))); setState(st); }
async function restoreSnap(g, snapId) { const s = await C.api.get(base(g) + '/snaps/' + snapId); if (!s) throw new Error('backup not found'); restoreLocal(g, s.data);
  const st = state(); st.seen = st.seen || {}; st.seen[g] = Math.max(st.seen[g] || 0, s.at); setState(st); toast(T('loadOk', { g: gName(g) })); setTimeout(() => location.reload(), 1200); }
async function checkNewer() { if (!active()) return;
  for (const g of C.games) { try { const m = await C.api.get(base(g)); const st = state(); if (!m || m.dev === device() || !(m.at > ((st.seen || {})[g] || 0))) continue;
      const local = localData(g); if (hash(JSON.stringify(local)) === m.hash) { st.seen = st.seen || {}; st.seen[g] = m.at; setState(st); continue; }
      if (g === 'game-hub' && hasProgress(g, local)) { st.seen = st.seen || {}; st.seen[g] = m.at; setState(st); continue; } // don't nag about hub settings
      const ok = await ask(T('newerT'), T('newerB', { g: gName(g), d: devName(m.kind), t: ago(m.at) }), T('load'), T('keep'));
      if (ok) { await restoreSnap(g, m.latest); return; }
      const s2 = state(); s2.seen = s2.seen || {}; s2.seen[g] = m.at; setState(s2);
    } catch (e) { C.err = (e && (e.code || e.message)) || '?'; chip(); } } }

/* ---------- friends: ask to join, approve ---------- */
const perm = e => /permission|insufficient/i.test(String((e && (e.code || e.message)) || ''));
const mailKey = e => String(e || '').trim().toLowerCase();
// family = may read users/{uid} and list requests; member = may read users/{uid}; guest = signed in with Google but not allowed.
// A network error leaves the role as it was (unknown counts as allowed, like before this feature).
async function detectRole() {
  if (!C.user) { C.role = null; return; } if (C.user.anon) { C.role = 'paired'; return; }
  try { await C.api.get('users/' + C.user.uid + '/ls/game-hub'); } catch (e) { if (!perm(e)) return; C.role = 'guest';
    try { C.myReq = await C.api.get('requests/' + C.user.uid); } catch (e2) { C.myReq = null; } return; }
  try { const l = await C.api.list('requests', 100); const before = C.reqs.length; C.reqs = l.filter(x => x && x.status === 'pending'); C.role = 'family';
    if (C.reqs.length > before && C.reqs.length) toast(T('newReq', { n: C.reqs.length })); }
  catch (e) { C.role = 'member'; C.reqs = []; } }
async function refreshRole() { const was = C.role; await detectRole(); chip();
  if (was === 'guest' && (C.role === 'member' || C.role === 'family')) { toast(T('welcome')); await checkNewer(); await uploadAll(false); }
  if (C.role === 'guest' && C.ask) { C.ask = false; guestMenu(); } }
async function sendMail(name) { const st = state(); st.mailed = st.mailed || {}; if (st.mailed[C.user.uid]) return false;
  const at = new Date(); let t = at.toISOString(); try { t = at.toLocaleString('en-CA', { timeZone: 'America/Toronto', dateStyle: 'medium', timeStyle: 'short' }) + ' (Montréal)'; } catch (e) {}
  try { const r = await C.api.mail({ service_id: MAIL.service, template_id: MAIL.template, user_id: MAIL.key,
      template_params: { friend_name: name, friend_email: C.user.email || '', time: t, hub_link: MAIL.hub } });
    if (r && r.ok) { st.mailed[C.user.uid] = Date.now(); setState(st); return true; } } catch (e) {} return false; }
async function apply() {
  const inp = document.createElement('input'); inp.type = 'text'; inp.maxLength = 40; inp.autocomplete = 'off'; inp.placeholder = T('namePh');
  inp.style.cssText = 'font:inherit;font-size:max(18px,1em);width:100%;padding:10px 12px;border:3px solid #1d3b25;border-radius:14px;margin:6px 0 12px;box-sizing:border-box';
  setTimeout(() => { try { inp.focus(); } catch (e) {} }, 50);
  const ok = await dialog(T('applyT'), T('applyB', { e: C.user.email || 'Google' }), [{ label: T('cancel'), value: false }, { label: T('send'), primary: true, value: true }], false, inp); if (!ok) return;
  const name = inp.value.replace(/\s+/g, ' ').trim().slice(0, 40); if (!name) { toast(T('nameNeed')); return apply(); }
  const doc = { uid: C.user.uid, email: C.user.email || '', name, at: Date.now(), status: 'pending', lang: lang() };
  try { await C.api.set('requests/' + C.user.uid, doc); } catch (e) { toast(T('err', { m: (e && (e.code || e.message)) || '?' })); return; }
  C.myReq = doc; chip(); toast(T('sent')); sendMail(name); }
async function guestMenu() {
  const r = C.myReq, e = C.user.email || 'Google';
  if (!r) { const v = await dialog(T('title'), T('applyB', { e }), [{ label: T('send'), wide: true, value: 'apply' }, { label: T('signOut'), wide: true, value: 'out' }, { label: T('close'), primary: true, value: null }], null);
    if (v === 'apply') return apply(); if (v === 'out') { try { await C.api.signOut(); } catch (x) {} } return; }
  const pend = r.status === 'pending';
  const v = await dialog(T('title'), pend ? T('pendingB', { e, t: ago(r.at) }) : T('deniedB', { e }), [...(pend ? [{ label: T('cancelReq'), wide: true, value: 'cancel' }] : []), { label: T('signOut'), wide: true, value: 'out' }, { label: T('close'), primary: true, value: null }], null);
  if (v === 'cancel') { try { await C.api.del('requests/' + C.user.uid); C.myReq = null; chip(); } catch (x) { toast(T('err', { m: (x && (x.code || x.message)) || '?' })); } }
  else if (v === 'out') { try { await C.api.signOut(); } catch (x) {} } }
async function friendsMenu() {
  try { await detectRole(); } catch (e) {} chip();
  if (!C.reqs.length) { await dialog(T('friendsT'), T('friendsNone'), [{ label: T('close'), primary: true, value: null }], null); return; }
  const q = C.reqs[0];
  const v = await dialog(T('friendsT') + (C.reqs.length > 1 ? ' · 1/' + C.reqs.length : ''), T('reqLine', { name: q.name || '?', email: q.email || '?', t: ago(q.at) }),
    [{ label: T('later'), value: null }, { label: T('deny'), value: 'no' }, { label: T('approve'), primary: true, value: 'yes' }], null);
  if (!v) return;
  try { if (v === 'yes') { await C.api.set('allowed/' + mailKey(q.email), { email: mailKey(q.email), name: q.name || '', uid: q.uid || '', at: Date.now(), by: C.user.uid });
        await C.api.set('requests/' + q.uid, Object.assign({}, q, { status: 'approved', done: Date.now() })); toast(T('approved', { name: q.name || '' })); }
      else { await C.api.set('requests/' + q.uid, Object.assign({}, q, { status: 'denied', done: Date.now() })); toast(T('denied', { name: q.name || '' })); }
  } catch (e) { toast(T('err', { m: (e && (e.code || e.message)) || '?' })); return; }
  C.reqs = C.reqs.filter(x => x !== q); chip(); if (C.reqs.length) return friendsMenu(); }
async function membersMenu() {
  let list = []; try { list = await C.api.list('allowed', 100); } catch (e) { toast(T('err', { m: (e && (e.code || e.message)) || '?' })); return; }
  const m = await dialog(T('membersBtn'), list.length ? '' : T('membersNone'), [...list.map(x => ({ label: (x.name || '?') + ' · ' + (x.email || x.id), wide: true, value: x })), { label: T('close'), primary: true, value: null }], null); if (!m) return;
  if (!(await ask(T('removeT'), T('removeB', { name: m.name || '?', email: m.email || m.id }), T('remove'), T('cancel')))) return;
  try { await C.api.del('allowed/' + (m.id || mailKey(m.email))); if (m.uid) { try { await C.api.del('requests/' + m.uid); } catch (e) {} } toast(T('removed', { name: m.name || '' })); } catch (e) { toast(T('err', { m: (e && (e.code || e.message)) || '?' })); } }

/* ---------- UI: chip, dialogs (touch + controller) ---------- */
const css = `.fc-chip{font:inherit;font-size:clamp(16px,1.46vw,28px);font-weight:700;min-height:44px;padding:6px 14px;border-radius:999px;border:3px solid #1d3b25;background:#fff8e1;color:#1d3b25;cursor:pointer}
.fc-chip.float{position:fixed;left:max(10px,env(safe-area-inset-left));bottom:max(10px,env(safe-area-inset-bottom));z-index:50;box-shadow:0 4px 0 rgba(0,0,0,.3)}
.fc-overlay{position:fixed;inset:0;background:rgba(10,20,12,.6);display:flex;align-items:center;justify-content:center;z-index:1000;padding:16px;touch-action:pan-y}
.fc-box{background:#fff8e1;color:#1d3b25;border:4px solid #1d3b25;border-radius:22px;padding:18px 20px;width:min(36em,100%);max-height:90vh;overflow:auto;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","PingFang TC","Microsoft YaHei",system-ui,sans-serif;font-size:clamp(18px,1.55vw,32px)}
.fc-box h2{margin:0 0 10px;font-size:1.35em}.fc-box p{white-space:pre-line;margin:6px 0 12px}.fc-row{display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end}
.fc-btn{font:inherit;font-size:1em;font-weight:700;min-height:2.6em;padding:8px 16px;border-radius:16px;border:3px solid #1d3b25;background:#f3e6bf;color:#1d3b25;cursor:pointer;flex:1 1 auto}
.fc-chip.fc-bell{background:#fee2e2;border-color:#b91c1c}.fc-btn.primary{background:#f59e0b}.fc-btn.wide{display:block;width:100%;text-align:left;margin:6px 0;flex:none}.fc-btn.fc-focus{outline:6px solid #f59e0b;outline-offset:3px;box-shadow:0 0 0 10px rgba(245,158,11,.35)}
.fc-toast{position:fixed;left:50%;top:16px;transform:translateX(-50%);background:rgba(29,59,37,.95);color:#fff;padding:10px 18px;border-radius:999px;font-weight:700;z-index:1001;max-width:92vw;text-align:center;font-family:system-ui,sans-serif}`;
function addCss() { if (document.getElementById('fc-css')) return; const s = document.createElement('style'); s.id = 'fc-css'; s.textContent = css; document.head.appendChild(s); }
function toast(m) { addCss(); const t = document.createElement('div'); t.className = 'fc-toast'; t.textContent = m; document.body.appendChild(t); setTimeout(() => t.remove(), 3500); }
let modal = null;
// a dialog: title, text, buttons [{label, primary, value}] -> Promise(value); B / ✕ resolves with cancelValue
function dialog(title, text, buttons, cancelValue, extra) { addCss(); return new Promise(res => {
  const o = document.createElement('div'); o.className = 'fc-overlay'; const b = document.createElement('div'); b.className = 'fc-box'; o.appendChild(b);
  const h = document.createElement('h2'); h.textContent = title; b.appendChild(h); if (text) { const p = document.createElement('p'); p.textContent = text; b.appendChild(p); }
  if (extra) b.appendChild(extra);
  const row = document.createElement('div'); row.className = 'fc-row'; b.appendChild(row);
  const done = v => { o.remove(); modal = null; res(v); };
  for (const bt of buttons) { const e = document.createElement('button'); e.type = 'button'; e.className = 'fc-btn' + (bt.primary ? ' primary' : '') + (bt.wide ? ' wide' : ''); e.textContent = bt.label;
    e.addEventListener('click', () => done(bt.value)); (bt.wide ? b.insertBefore(e, row) : row.appendChild(e)); }
  document.body.appendChild(o); modal = { el: o, cancel: () => done(cancelValue), btns: [...b.querySelectorAll('.fc-btn')], i: 0 };
  const pi = modal.btns.findIndex(x => x.classList.contains('primary')); modal.i = pi >= 0 ? pi : 0; mark(); }); }
function mark() { if (!modal) return; modal.btns.forEach((x, i) => x.classList.toggle('fc-focus', i === modal.i)); try { modal.btns[modal.i].focus({ preventScroll: false }); } catch (e) {} }
const ask = (title, text, yes, no) => dialog(title, text, [{ label: no, value: false }, { label: yes, primary: true, value: true }], false);
// controller inside our dialogs (the hub's own navigation pauses while one is open)
let prev = {};
function pollPads() { let pads = []; try { pads = Array.from((navigator.getGamepads && navigator.getGamepads()) || []).filter(Boolean); } catch (e) {}
  for (const gp of pads) { const btn = i => !!(gp.buttons[i] && gp.buttons[i].pressed), ax = gp.axes || [];
    const now = { a: btn(0), b: btn(1), up: btn(12) || ax[1] < -0.55, down: btn(13) || ax[1] > 0.55, left: btn(14) || ax[0] < -0.55, right: btn(15) || ax[0] > 0.55 };
    const p = prev[gp.index] || {}; prev[gp.index] = now; if (!modal) continue;
    if (!modal.armed) { if (!now.a && !now.b) modal.armed = true; continue; } // the press that opened the dialog must not also answer it
    const hit = k => now[k] && !p[k];
    if (hit('a')) modal.btns[modal.i].click(); else if (hit('b')) modal.cancel();
    else if (hit('up') || hit('left')) { modal.i = (modal.i - 1 + modal.btns.length) % modal.btns.length; mark(); }
    else if (hit('down') || hit('right')) { modal.i = (modal.i + 1) % modal.btns.length; mark(); } }
  requestAnimationFrame(pollPads); }
document.addEventListener('keydown', e => { if (!modal) return; if (e.key === 'Escape') { modal.cancel(); e.preventDefault(); } }, true);
let chipEl = null;
function chip() { if (!chipEl) return; const bell = C.role === 'family' && C.reqs.length ? '🔔 ' + C.reqs.length + ' · ' : ''; chipEl.classList.toggle('fc-bell', !!bell); chipEl.textContent = bell + (!C.api ? '' : C.role === 'guest' ? (C.myReq && C.myReq.status === 'pending' ? T('pendingChip') : T('guestChip')) : !active() ? T('chipOff') : C.busy ? T('chipBusy') : C.err ? T('chipErr') : (Object.keys(state().up || {}).length ? T('chipOn', { t: ago(Math.max(0, ...Object.values(state().up || {}))) }) : T('chipReady'))); chipEl.hidden = !C.api; }
async function menu() {
  if (C.role === 'guest' && C.user && !C.user.anon) return guestMenu();
  if (!active()) { const home = homeApp(), g = { label: T('signIn'), wide: true, value: 'g' }, p = { label: T('pairStart'), wide: true, value: 'p' };
    const v = await dialog(T('title'), home ? T('homeB') : T('signedOut'), [...(home ? [p, g] : [g, p]), { label: T('close'), primary: true, value: null }], null);
    if (v === 'g') signIn(); else if (v === 'p') pairThisDevice(); return; }
  const st = state(); const lines = C.games.filter(g => g !== 'game-hub').map(g => T('lastUp', { g: gName(g), t: ago((st.up || {})[g]) }));
  const who = C.user.anon ? T('pairedAs', { e: state().ownerEmail || '?' }) : T('as', { e: C.user.email || 'Google' });
  const text = who + '\n' + lines.join('\n') + (C.err ? '\n' + T('err', { m: C.err }) : '') + '\n' + T('drawrassic');
  const v = await dialog(T('title'), text, [{ label: T('upAll'), wide: true, value: 'up' }, { label: T('restore'), wide: true, value: 'restore' }, ...(C.role === 'family' ? [{ label: T('friendsBtn', { n: C.reqs.length }), wide: true, value: 'friends' }, { label: T('membersBtn'), wide: true, value: 'members' }] : []), ...(C.user.anon ? [] : [{ label: T('pairOther'), wide: true, value: 'pair' }]), { label: C.user.anon ? T('unpair') : T('signOut'), wide: true, value: 'out' }, { label: T('close'), primary: true, value: null }], null);
  if (v === 'up') { await uploadAll(true); if (!C.err) toast(T('upOk')); else toast(T('err', { m: C.err })); }
  else if (v === 'out') { if (C.user.anon) setState({ owner: null, ownerEmail: null }); try { await C.api.signOut(); } catch (e) {} chip(); }
  else if (v === 'pair') pairOtherDevice();
  else if (v === 'friends') friendsMenu();
  else if (v === 'members') membersMenu();
  else if (v === 'restore') {
    const g = await dialog(T('pickGame'), '', [...C.games.filter(x => x !== 'game-hub').map(x => ({ label: gName(x), wide: true, value: x })), { label: T('close'), value: null }], null); if (!g) return;
    let list = []; try { list = await C.api.list(base(g) + '/snaps', 80); } catch (e) { toast(T('err', { m: (e && (e.code || e.message)) || '?' })); return; }
    const seen = new Set(), items = []; for (const s of list) { if (seen.has(s.at)) continue; seen.add(s.at); items.push({ label: new Date(s.at).toLocaleString() + ' · ' + devName(s.kind), wide: true, value: s }); }
    const s = await dialog(T('pickSnap'), items.length ? '' : T('none'), [...items, { label: T('close'), value: null }], null); if (!s) return;
    if (await ask(T('confirmT'), T('confirmB', { g: gName(g), d: devName(s.kind), t: new Date(s.at).toLocaleString() }), T('load'), T('close'))) { try { await restoreSnap(g, s.id); } catch (e) { toast(T('err', { m: (e && (e.code || e.message)) || '?' })); } } } }

/* ---------- pairing: a device that can't sign in to Google (Xbox) borrows the family's cloud saves ---------- */
const CODE_CHARS = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';   // no 0/O, 1/I/L
const PAIR_TTL = 10 * 60000;
async function pairThisDevice() {
  try { if (!C.user || !C.user.anon) await C.api.signInAnon(); } catch (e) { toast(T('err', { m: (e && (e.code || e.message)) || '?' })); return; }
  for (let i = 0; i < 50 && !(C.user && C.user.anon); i++) await new Promise(r => setTimeout(r, 100));
  if (!(C.user && C.user.anon)) { toast(T('err', { m: 'anonymous sign-in' })); return; }
  let code = ''; for (let i = 0; i < 6; i++) code += CODE_CHARS[Math.floor(Math.random() * CODE_CHARS.length)];
  try { await C.api.set('pairing/' + code, { anon: C.user.uid, at: Date.now(), kind: devKind() }); } catch (e) { toast(T('err', { m: (e && (e.code || e.message)) || '?' })); return; }
  const big = document.createElement('div'); big.style.cssText = 'font:900 clamp(48px,6vw,120px)/1.1 ui-monospace,Menlo,monospace;letter-spacing:.15em;text-align:center;margin:10px 0;color:#1d3b25'; big.textContent = code;
  const wait = document.createElement('div'); wait.style.cssText = 'text-align:center;opacity:.8;margin:4px 0 14px'; wait.textContent = T('pairWait'); big.appendChild(document.createElement('br'));
  const box = document.createElement('div'); box.append(big, wait);
  let done = false; const t0 = Date.now();
  const watcher = (async () => { while (!done) { await new Promise(r => setTimeout(r, 2000)); if (done) return;
      if (Date.now() - t0 > PAIR_TTL) { done = true; modal && modal.cancel(); toast(T('pairOld')); return; }
      try { const d = await C.api.get('pairing/' + code); if (d && d.owner) { done = true; setState({ owner: d.owner, ownerEmail: d.ownerEmail || '' }); try { await C.api.del('pairing/' + code); } catch (e) {}
          modal && modal.cancel(); toast(T('pairOk', { e: d.ownerEmail || '' })); chip(); await checkNewer(); await uploadAll(false); return; } } catch (e) {} } })();
  await dialog(T('pairT'), T('pairB'), [{ label: T('cancel'), primary: true, value: null }], null, box); done = true; await watcher; }
async function pairOtherDevice() {
  const inp = document.createElement('input'); inp.type = 'text'; inp.autocapitalize = 'characters'; inp.autocomplete = 'off'; inp.maxLength = 6; inp.inputMode = 'text';
  inp.style.cssText = 'font:900 max(36px,1.6em) ui-monospace,Menlo,monospace;letter-spacing:.2em;text-transform:uppercase;width:100%;padding:8px 12px;border:3px solid #1d3b25;border-radius:14px;margin:6px 0 12px';
  setTimeout(() => { try { inp.focus(); } catch (e) {} }, 50);
  const ok = await dialog(T('pairOther'), T('pairEnter'), [{ label: T('cancel'), value: false }, { label: T('ok'), primary: true, value: true }], false, inp); if (!ok) return;
  const code = inp.value.trim().toUpperCase().replace(/[^A-Z0-9]/g, '');
  try { const d = await C.api.get('pairing/' + code); if (!d || !d.anon || Date.now() - (d.at || 0) > PAIR_TTL) { toast(T('pairBad')); return; }
    await C.api.set('users/' + C.user.uid + '/devices/' + d.anon, { at: Date.now(), kind: d.kind || 'other' });
    await C.api.set('pairing/' + code, Object.assign({}, d, { owner: C.user.uid, ownerEmail: C.user.email || '' })); toast(T('pairDone'));
  } catch (e) { toast(T('err', { m: (e && (e.code || e.message)) || '?' })); } }
// iPad Home Screen apps: the Google pop-up opens in a separate sheet that can't hand its result back, so sign-in ends as
// "popup closed" (which used to be silent). Explain it there and offer the pairing code instead.
function homeApp() { try { return navigator.standalone === true || matchMedia('(display-mode: standalone)').matches; } catch (e) { return false; } }
async function homeHelp() { const v = await dialog(T('title'), T('homeB'), [{ label: T('pairStart'), wide: true, value: 'p' }, { label: T('close'), primary: true, value: null }], null); if (v === 'p') pairThisDevice(); }
async function signIn() { C.ask = true; try { await C.api.signIn(); } catch (e) { const c = (e && (e.code || e.message)) || '?';
  if (homeApp() && !(C.user && !C.user.anon)) return homeHelp();
  if (!/popup-closed|cancelled-popup/.test(c)) toast(T('err', { m: c })); } }

/* ---------- start ---------- */
async function start() {
  C.games = ((ME && ME.dataset.games) || '').split(',').map(s => s.trim()).filter(g => GAMES[g]);
  C.chip = (ME && ME.dataset.chip) || 'float';
  if (C.chip !== 'none') { addCss(); chipEl = document.createElement('button'); chipEl.type = 'button'; chipEl.className = 'fc-chip' + (C.chip === 'hub' ? ' btn nav' : ' float'); chipEl.dataset.key = 'family-cloud'; chipEl.hidden = true;
    chipEl.addEventListener('click', menu);
    const slot = C.chip === 'hub' && document.querySelector('header'); if (slot) slot.appendChild(chipEl); else document.body.appendChild(chipEl); }
  requestAnimationFrame(pollPads);
  try { C.api = await loadApi(); } catch (e) { C.api = null; chip(); return; }
  C.api.onUser(async u => { C.user = u; C.role = null; C.reqs = []; C.myReq = null; if (u && !u.anon && state().owner) setState({ owner: null, ownerEmail: null });
    if (u) { try { await detectRole(); } catch (e) {} } chip(); if (C.role === 'guest' && C.ask) { C.ask = false; guestMenu(); } if (active()) { await checkNewer(); await uploadAll(false); } });
  setInterval(() => { if (C.user && !C.user.anon && !document.hidden && C.role !== 'paired') refreshRole().catch(() => {}); if (active() && !document.hidden) uploadAll(false); else chip(); }, CFG.checkEveryMs);
  document.addEventListener('visibilitychange', () => { if (!document.hidden && C.user && !C.user.anon && C.role !== 'paired') refreshRole().catch(() => {}); if (!active()) return; if (document.hidden) uploadAll(false); else checkNewer(); });
  window.addEventListener('pagehide', () => { if (active()) uploadAll(false); });
  chip(); }
window.FamilyCloud = { menu, isModalOpen: () => !!modal, uploadAll: () => uploadAll(true), role: () => C.role, pending: () => C.reqs.length };
if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
