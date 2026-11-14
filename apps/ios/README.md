# Drawrassic Park iOS App（Capacitor）

把 `drawrassic-park/` 里的游戏打包成一个 iPad App。游戏文件**打进 App 里**，不加载任何网址，断网也能玩。

- `drawrassic-park/` 里的文件**只读不改**。打包脚本把它们复制到 `www/`，然后只在副本上做修改。
- 上架 App Store 需要准备什么，见 [APP-STORE.md](APP-STORE.md)。
- 隐私政策页面：[privacy/index.html](privacy/index.html)，四种语言。推送到 main 后的地址是 `https://family-games-hub.vercel.app/apps/ios/privacy/`。

## 目录

| 路径 | 作用 |
|---|---|
| `scripts/build-www.mjs` | 从 `drawrassic-park/` 生成 `www/`：复制最新版本，去掉 Google Fonts、改成打包进来的 Fredoka 字体，注入 App 外壳。打补丁对不上就直接报错退出。 |
| `shell/app-shell.js` / `.css` | App 外壳：`window.FamilyNative` 接口、拦外链、去网页痕迹、隐藏网页专用的界面 |
| `ios/App/App/FamilyNative.swift` | 原生插件：Game Center、触感震动、iCloud 存档、存图到相册、剪贴板、导航拦截 |
| `ios/App/App/Info.plist`、`*.lproj/InfoPlist.strings` | 权限说明（四种语言）、隐藏状态栏、手柄支持、加密声明 |
| `ios/App/App/PrivacyInfo.xcprivacy` | 隐私清单：不追踪、不收集数据 |
| `tests/test_www.py` | 在 Chrome 里断网测试 `www/`，iPad 两种尺寸 |
| `privacy/` | 隐私政策网页（填进 App Store Connect 用） |
| `www/`、`node_modules/` | 生成的文件，不进 git |

### 两种打包方式（profile）

| | `store`（默认） | `family` |
|---|---|---|
| 命令 | `npm run sync` | `npm run sync:family` |
| 用途 | 上架 App Store（儿童分类） | TestFlight 发给家人 |
| 联网 | 完全不联网 | 只有 🌐 联机对战 / 一起玩会连 PeerJS 公共服务器 |
| 联机房间、文字聊天 | 入口隐藏 | 保留 |
| 语音聊天 | 关闭 | 关闭（App 不申请麦克风） |
| 云备份（Google 登录）、切换版本、全屏按钮 | 隐藏 | 隐藏 |

`store` 版隐藏联机入口是靠 CSS 选择器（`#netOpen`、快捷栏的 `[data-qa=online|together|players]`），只能尽量做到。"一起玩"的入口散落在很多地方，快捷栏编辑器里可能还看得到它的名字，但点了只会提示"这里不能连线"。如果要彻底去掉，请在下一个游戏版本里读 `window.FAMILY_APP.online`，把这些入口全部隐藏，详见 APP-STORE.md 的"联机聊天和语音"一节。

### `window.FamilyNative`（游戏可以调用的原生接口）

每个调用都返回 Promise，**永远不会 reject**，结果是 `{ok: true, ...}` 或 `{ok: false, reason}`。在网页版（不在 App 里）调用会得到 `reason: 'not-native'`，所以游戏可以直接检测，不需要分版本。

```js
if (window.FamilyNative && FamilyNative.isNative()) { ... }
FamilyNative.app                          // {platform:'ios', profile:'store'|'family', online, gameVersion, ...}
FamilyNative.info()                       // App 版本、iCloud 是否登录、Game Center 状态
FamilyNative.haptic('light'|'medium'|'heavy'|'soft'|'rigid'|'success'|'warning'|'error'|'selection')
FamilyNative.gameCenter.signIn()          // → {ok, underage, multiplayerRestricted, communicationRestricted}
FamilyNative.gameCenter.submitScore('leaderboard.id', 1234)
FamilyNative.gameCenter.reportAchievement('achievement.id', 100)
FamilyNative.gameCenter.showDashboard('achievements'|'leaderboards'|'default')
FamilyNative.cloud.status() / save(key, text) / load(key) / list()   // iCloud Drive 里 App 自己的容器
FamilyNative.photos.saveImage(dataUrl | canvas | Blob)               // 只申请“添加照片”权限
FamilyNative.copyText(text)
```

下面这些**不用改游戏**就已经生效：
- 游戏调用 `navigator.vibrate(...)` 会转成原生触感反馈。**但 iPad 本身没有触感马达（Taptic Engine），所以在 iPad 上不会有任何感觉。** 这个接口留给以后的 iPhone 版用。Apple Pencil Pro 的触感需要另一套 API，目前没做。Xbox 手柄的震动走的是游戏自己的 Gamepad 代码，和这个接口无关。
- "⬇️ PNG" 这种下载链接会改成**存到相册**，并在屏幕上显示四种语言的提示。
- `navigator.clipboard.writeText` 失败时（WebKit 有时会拒绝）改用原生剪贴板，保证"复制备份码"能用。

iCloud 存档的接口已经准备好了，但游戏还没有调用它。下一个游戏版本可以在"复制备份码"旁边加一个"☁️ 存到 iCloud"按钮，调用 `FamilyNative.cloud.save('backup', exportCode())`。

## ⚠️ 存档：App 有自己独立的存储

App 里的游戏数据和 Safari、主屏幕图标版的数据**互不相通**，就像又多了一个新的主屏幕图标。第一次在 iPad 上装 App 时，请按这个顺序做：

1. 在原来玩的地方（Safari 或主屏幕图标），点 ⚙️ →“复制备份码”，再贴到"备忘录"里存一份。
2. 安装 App，然后打开。
3. App 会问"以前玩过吗？"，选"导入我的备份"，把备份码贴进去。
4. 检查恐龙和画作是否都在。
5. 确认无误后，旧的主屏幕图标可以留着当备用，不要急着删。

另外：
- **删除 App 会删除 App 里的所有存档。** "卸载 App"（iPad 设置里的"卸载未使用的 App"）则会保留数据。
- TestFlight 版和 App Store 版用的是同一个 Bundle ID，互相替换时数据一般会保留。但 Apple 的 TestFlight 条款说，在已经安装正式版的设备上装测试版，数据可能丢失。所以每次切换之前，都先复制备份码。

## 在 Mac 上第一次编译

### 需要准备
- **macOS**：Xcode 26.0–26.3 需要 macOS Sequoia 15.6 以上，Xcode 26.4 以后需要 macOS Tahoe 26.2 以上。从 4 月 28 日起，上传到 App Store 的 App 必须用 Xcode 26 编译。2013 年的圆筒 Mac Pro 装不了这么新的系统，2019 年的 Mac Pro 可以。查看方法：左上角  → 关于本机。
- **Xcode**：从 Mac App Store 安装，装完打开一次，同意许可并装好 iOS 组件。Capacitor 8 至少要 Xcode 26。
- **Node.js 22** 或更新版本（Capacitor 8 的要求）。
- **iPad**：iPadOS 15 或更新。

### 步骤
```bash
git clone https://github.com/jacobjkwu/family-games.git
cd family-games/apps/ios
npm install
npm run sync            # 生成 www/ 并复制进 Xcode 项目（App Store 版）
# 或者 npm run sync:family   （家人用的 TestFlight 版，带联机）
npm run open            # 用 Xcode 打开 ios/App/App.xcodeproj
```
第一次打开时，Xcode 会自动下载 Capacitor 的 Swift Package，需要等一两分钟（左边栏会显示 Package Dependencies）。

### 在 Xcode 里设置一次
1. 左边点蓝色的 **App** 项目 → TARGETS 选 **App** → **Signing & Capabilities**。
2. 勾选 **Automatically manage signing**，**Team** 选你的开发者团队。如果列表里没有，先去 Xcode → Settings → Accounts 登录 Apple 账户。
3. **Bundle Identifier** 目前是 `com.jacobwu.drawrassicpark`。它必须全球唯一，在 App Store Connect 建好 App 之后就不能再改了，现在可以换成你想要的。如果改了，也要同步改 `capacitor.config.json` 里的 `appId`。
4. 版本号在 **General** → Identity：Version（例如 1.0）、Build（每次上传都要加 1）。

## 装到 iPad 上

1. 用数据线把 iPad 连到 Mac，在 iPad 上点"信任这台电脑"。
2. 在 Xcode 顶部的设备列表里选你的 iPad。第一次用时，iPad 会提示打开**开发者模式**：设置 → 隐私与安全性 → 开发者模式 → 打开，然后重启 iPad。
3. 点 ▶︎（Run）。第一次安装后，如果打开 App 提示"不受信任的开发者"，就去 设置 → 通用 → VPN 与设备管理 里信任它。

**免费 Apple 账户和付费开发者账户的区别**：
- 免费账户（Personal Team）也能装到自己的 iPad 上，但 **7 天后就打不开了**，要重新用 Xcode 装一次（存档还在）。免费账户不能用 Game Center、iCloud，也不能用 TestFlight。
- 付费账户（每年 99 美元）可以用全部功能，开发版本有效期也长得多。

## 打开 Game Center 和 iCloud（需要付费账户）

代码已经写好。在 Xcode 里加上对应的 capability 之后才会生效，没加之前调用会返回 `reason: 'unavailable'` 或 `'not-signed-in'`，游戏不受影响。

1. **Signing & Capabilities** → 左上角 **+ Capability** → 添加 **Game Center**。
2. 再点 **+ Capability** → 添加 **iCloud** → 勾选 **iCloud Documents** → 在 Containers 里点 **+**，新建 `iCloud.<你的 Bundle ID>`，并勾选它。
3. Xcode 会自动生成 `App.entitlements`，并更新描述文件。把这个文件提交到 git。
4. Game Center 的排行榜和成就要在 App Store Connect → 你的 App → **Game Center** 里建好，ID 要和游戏调用的一致。

## 用 TestFlight 发给家人

1. 先在 App Store Connect 建好 App（见 APP-STORE.md 第 2 步）。
2. 在 Mac 上运行 `npm run sync:family`（或者 `npm run sync`）。
3. Xcode 顶部设备选 **Any iOS Device (arm64)** → 菜单 **Product → Archive**。
4. 编译完成后会打开 Organizer → **Distribute App** → **App Store Connect** → Upload。
5. 等 10–30 分钟处理完成，到 App Store Connect → **TestFlight** 标签页查看。
6. 加测试员：
   - **内部测试**：最多 100 人，必须是你 App Store Connect 团队的成员（在"用户和访问"里邀请，比如另一位家长）。**不需要审核**，上传后马上能装。
   - **外部测试**：最多 10,000 人，用邮件邀请或公开链接。每个新版本的第一个 build 要先通过 Apple 的 Beta 审核（通常一两天）。
7. 家人在 iPad 上安装 **TestFlight** App，打开邀请邮件或链接，点"安装"。
8. TestFlight 的 build **90 天后过期**，到期前需要上传新的 build。

**⚠️ 13 岁以下不能用 TestFlight。** Apple 的条款不允许 13 岁以下的孩子使用 TestFlight。如果孩子的 iPad 登录的是家人共享里的儿童账户，就装不了。可以这样做：
- **家长账户**：在孩子 iPad 的 设置 → App Store 里改用家长的 Apple 账户（只影响下载 App 的账户，iCloud 账户可以保持不变），然后用家长账户装 TestFlight 版。
- **用数据线从 Xcode 直接装**：按上面"装到 iPad 上"的步骤操作。付费账户的开发版本可以用很久，过期了重装一次就行，存档还在。

## 游戏出了新版本以后

`drawrassic-park/versions.json` 里最上面那个版本就是"最新版"。
```bash
cd apps/ios
npm run test:web        # 生成 www/ 并在 Chrome 里断网测试（需要 python3 + playwright + Chrome）
npm run sync            # 复制进 Xcode
```
然后在 Xcode 里把 **Build** 号加 1，再执行 Archive → 上传。
- 想打包某个旧版本：`node scripts/build-www.mjs --version 3.72 && npx cap sync ios`。
- 如果新版本改了 HTML，打包脚本或 `test_www.py` 会报错，并告诉你哪一处对不上。修 `scripts/build-www.mjs` 或 `shell/app-shell.css`，**不要改** `drawrassic-park/` 里的文件。

## 测过什么，没测过什么

- ✅ 在 Linux 的 Chrome 里测试了 `www/`（store 和 family 两种版本）：分别用 1180×820 和 820×1180、开触屏模拟；除本地以外的请求全部拦掉；Capacitor 原生桥是模拟的。测试项包括：启动后直接进游戏、零外部请求、没有页面错误、Fredoka 字体加载成功、网页专用的界面被隐藏、外链和 `window.open` 被拦、`navigator.vibrate` 转成原生触感、下载链接转成存相册（提示文字四种语言都对）、🛟 救援页能打开也能返回游戏。还测了 family 版能从本地加载 PeerJS。
- ❌ **Swift 代码没有编译过**。这个会话在 Linux 上，没有 Xcode。第一次在 Mac 上编译时，如果报错，把错误信息发给我。
- ❌ 没有在真实的 WKWebView、真 iPad、TestFlight 上测试过。Game Center、iCloud、存相册都需要在真机上验证。
- ❌ 没有测试 App 里的联机（family 版）。WKWebView 支持 WebRTC，但没有在真机上连过。
- ❌ 没有用 Xbox 手柄连 iPad 测过 App 版。
