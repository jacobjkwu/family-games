# Drawrassic Park 上架 App Store 清单

以下根据 2026 年 11 月查到的 Apple 规则整理，规则会变，提交前请再看一遍 [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)。

## 1. 账户和工具
- [ ] 加入 Apple Developer Program（个人，年费 99 美元），用 Apple Developer App 报名。个人账户会在 App Store 上**公开显示法定姓名**。
- [ ] 登录 App Store Connect（appstoreconnect.apple.com），同意里面的协议。免费 App 不需要填付款和税务信息。
- [ ] Mac 上装 **Xcode 26 或更新版本**。从 2026 年 4 月 28 日起，上传的 App 必须用 Xcode 26 和 iOS 26 SDK 编译。
- [ ] 如果要在欧盟上架：在 App Store Connect 里声明是不是"交易商"（trader）。选"是"的话，地址和电话会公开显示；家庭非商业项目一般选"否"。

## 2. 在 App Store Connect 里建 App
- [ ] "我的 App" → **+** → 新建 App：平台选 iOS，名称、主要语言、Bundle ID（和 Xcode 里的一致）、SKU（随便填，比如 `drawrassic-park`）。
- [ ] **名称风险**："Drawrassic Park" 是在模仿 *Jurassic Park*（环球影业的商标），可能会因为商标被拒，或者以后收到投诉。建议准备一个备用名，比如"Draw-a-Saurus Park"或"恐龙画画乐园"，"Drawrassic Park"可以留在副标题或描述里。
- [ ] 本地化：英文、法文、简体中文、繁体中文，每种语言单独填名称、副标题和描述。

## 3. 截图和图标
- [ ] **iPad 13 英寸**截图（项目设为只支持 iPad，所以**不需要 iPhone 截图**）。尺寸可选：横屏 **2752×2064** 或 2732×2048，竖屏 2064×2752 或 2048×2732。格式 PNG 或 JPG，每种语言 1–10 张。
  - 截图来源：可以在 iPad Pro 13 英寸模拟器里截（⌘S），也可以用 Chrome 打开 `www/`，设成 1376×1032、DPR 2 来截。需要的话，我可以写脚本按四种语言自动生成。
  - 截图里**不要出现**"For Kids"之类的字样，除非你真的选了儿童分类（规则 2.3.8）。也不要出现 Jurassic Park 的标志或类似图案。
- [ ] App 图标 1024×1024（已经放在 `Assets.xcassets/AppIcon`）。⚠️ 现在这个是从 512px 放大的，看起来会有点糊。最好用原始画稿重新导出一张 1024px 的，图片不能有透明通道。
- [ ] 可选：App 预览视频（尺寸必须和 13 英寸截图一样）。

## 4. 文字信息
- [ ] 副标题（最多 30 个字符），例如：Draw dinos. Watch them live.
- [ ] 描述、关键词（最多 100 个字符）、"新功能"说明。
- [ ] **支持网址**（必填）：可以用 GitHub 仓库的 Issues 页面，或者一个简单的说明页。**不要把家人的邮箱写进公开仓库。**
- [ ] **隐私政策网址**（必填，儿童类 App 更是必须有）：`https://family-games-hub.vercel.app/apps/ios/privacy/`。这一页在 `apps/ios/privacy/index.html`，要等这个分支合并到 main、Vercel 部署之后才能访问。页面里的"联系方式"写的是"用 App Store 页面上的 App 支持链接"，所以要确保支持网址能联系到你。
- [ ] 版权：例如 `2026 <你的法定姓名>`。
- [ ] 类别：如果走儿童分类，**主要类别选 Kids** 并选年龄段，次要类别选 Games；如果不走儿童分类，主要类别选 Games，子类别可以选 Family 或 Casual。

## 5. 要不要进"儿童"分类（Kids Category）
进儿童分类会在 App Store 的"儿童"区出现，但要求严格得多。规则 1.3 的要求如下：
- 不能有指向 App 外的链接、购买机会，或其他会分散孩子注意力的东西，除非放在**家长门**（parental gate）后面。
- 不能把个人信息或设备信息发给第三方，不能有第三方统计或第三方广告。
- 要从这三个年龄段里选一个：**5 岁及以下、6–8 岁、9–11 岁**。Drawrassic Park 内容多、文字多，建议选 **6–8 岁**或 **9–11 岁**。

规则 5.1.4 还规定：只要 App 会收集、传输或能够分享未成年人的个人信息，就必须有隐私政策，并遵守各地的儿童隐私法（比如美国的 COPPA）。这里说的个人信息**明确包括画作、照片、聊天能力**。

**`store` 版目前的状况：**
- ✅ 不联网，没有任何第三方服务或 SDK；`PrivacyInfo.xcprivacy` 里声明了不追踪、不收集数据。
- ✅ 外链在 App 外壳和原生层都会被拦掉（`window.open`、`<a target=_blank>`、mailto 都试过，都不会离开 App）。
- ✅ 没有内购，没有广告。
- ✅ 照片：只在玩家点"⬇️ PNG"时请求"添加照片"权限，从不读取相册。
- ⚠️ **申请权限算不算"需要家长门"**：Apple 对儿童类 App 的说明里提到，链接外部、**申请权限**、出现购买机会，都应该放在家长门后面。存相册时 iOS 会弹出系统权限对话框。为了保险，下一个游戏版本可以在第一次存图前加一个家长门，比如一道简单的算术题。
- ⚠️ 联机入口是靠 CSS 隐藏的（见下面第 7 节）。正式提交前，最好让游戏自己根据 `FAMILY_APP.online === false` 去掉这些入口。

**不进儿童分类**也是可以的：作为普通游戏上架，年龄分级照常填。限制少很多，只是不会出现在"儿童"区，而且描述里**不能**写"For Kids"（规则 2.3.8）。

## 6. 年龄分级问卷（App 信息 → 年龄分级）
现在的分级是 4+、9+、13+、16+、18+，由你回答的问卷自动算出来。问卷包括"App 内控制"和"功能"（家长控制、年龄验证、网页访问、用户生成内容、消息与聊天、广告、社交媒体），以及各类内容出现的频率。

按 `store` 版回答：
- 网页访问：**否**（外链全部被拦）。
- 用户生成内容：画作只保存在本机，不分享给别人，所以答**否**。
- 消息与聊天：**否**（store 版没有聊天）。如果以后加了任何形式的聊天，这里要改成"是"。
- 广告：否。社交媒体：否。
- 卡通或幻想暴力：游戏里有打架、Boss、"暴怒"之类的玩法，选**轻微/不频繁**，最终分级一般会是 4+ 或 9+。请按实际内容诚实回答（规则 2.3.6）。
- 竞赛、赌博：否。

## 7. 联机聊天和语音在儿童分类下怎么处理
游戏 v3.73 现在有两种联机：🌐 联机军团对战，以及 🌐 一起玩（开放公园、👥 玩家列表、💬 文字聊天、🎤 语音）。它们都通过免费的 PeerJS 公共服务器（0.peerjs.com）建立 WebRTC 连接。

问题出在哪里：
1. **第三方**：PeerJS 公共服务器不是你的，它能看到连接双方的 IP 地址和房间 ID。WebRTC 连接本身也会把 IP 地址暴露给对方。这和"不能把设备信息发给第三方"（规则 1.3）冲突。
2. **聊天是个人信息**：规则 5.1.4 把"聊天能力"列为个人信息。孩子打的字可能包含姓名、学校、地址；**语音**在 COPPA 里也属于个人信息。
3. **用户生成内容的管理要求**（规则 1.2）：有聊天就必须有过滤不良内容、举报、拉黑和公开的联系方式。现在的游戏有"请离开"和"加入前要我同意"，但没有过滤和举报。规则 1.2 还明确禁止随机或匿名聊天。

**建议的处理方式（从简单到复杂）：**

| 方案 | 怎么做 | 适合 |
|---|---|---|
| **A. 上架版不联机（现在就是这样）** | `store` 版不打包 PeerJS，隐藏入口，关掉麦克风，不申请麦克风权限 | ✅ 首次上架，儿童分类 |
| B. 家人内部联机 | 用 `family` 版通过 TestFlight 发给家人，联机和文字聊天照常，语音关闭 | ✅ 现在就能用；TestFlight 不在儿童分类里 |
| C. 上架版加"安全联机" | ① 改用 Game Center 好友和配对（GameKit），Apple 的屏幕使用时间和家长控制会自动生效，原生接口里的 `signIn()` 已经会返回 `multiplayerRestricted` 和 `communicationRestricted`；② **不开放自由打字**，只提供预设的短语和表情（比如"👋 你好"、"🦖 来看我的恐龙"），通过消息 ID 发送，正好符合"只发动作 ID、不发翻译后文字"的规则；③ **不做语音**；④ 进入联机前加家长门；⑤ 不再用 PeerJS 公共服务器，改用自己的中继服务器，或者走 Game Center | 以后的版本 |
| D. 保留自由聊天 | 要做过滤、举报、拉黑、公开联系方式，问卷里"消息与聊天"答"是"，还要处理 COPPA 规定的家长同意。**不建议在儿童分类里这样做。** | ❌ |

总结：**儿童分类的上架版不要有自由文字聊天，也不要有语音。** 如果想联机，就用 Game Center 好友加预设短语，并放在家长门后面。家人之间的完整联机用 TestFlight 的 `family` 版。

## 8. App 隐私（"营养标签"）
- `store` 版：**不收集数据**（Data Not Collected）。游戏数据只存在本机，开发者收不到任何东西。
- 如果以后启用 iCloud 和 Game Center：这两项由 Apple 用玩家自己的账户处理，开发者拿不到数据。不过提交前请对照 App Store Connect 里的说明，确认这两项不需要申报。我没有找到 Apple 关于这一点的明确说法。
- `family` 版如果要做外部 TestFlight 测试：PeerJS 公共服务器会看到 IP 地址。TestFlight 本身不要求填隐私标签，但"Beta 版 App 说明"里最好写明这一点。

## 9. 审核备注（App Review Information）
- 联系人姓名和电话：这些只有 Apple 能看到。
- 不需要演示账号（App 没有登录）。
- 备注可以这样写：
  > Offline drawing game for iPad. All game files are bundled; the store build makes no network connections. No accounts, ads, analytics or in-app purchases. Photos permission (add-only) is requested only when the player taps "⬇️ PNG" to save a picture.
- ⚠️ **规则 4.2（最低功能要求）**：用网页技术做的 App，有时会被认为"只是把网站包装了一下"。这款游戏是完整的离线游戏，所有内容都打包在 App 里，还有原生功能（存相册、手柄、iCloud 和 Game Center 接口），风险不大。如果被拒，回复时强调这几点就行。

## 10. 提交前最后检查
- [ ] `npm run test:web` 全部通过。
- [ ] 在真 iPad 上用 TestFlight 装 `store` 版，开飞行模式玩一遍：新公园、画恐龙、存档、杀掉 App 重开存档还在、复制备份码、导入备份、🛟 救援页、存图到相册、四种语言、横竖屏切换、Xbox 手柄（如果有）。
- [ ] Xcode 里 Build 号已经加 1，Version 也正确。
- [ ] 隐私政策网址能打开（main 分支已经部署）。
- [ ] 截图、描述四种语言都填好了。
- [ ] 年龄分级问卷和 App 隐私都填了。
- [ ] 选 build → **添加以供审核** → 提交。审核通常一两天。

来源：[App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)、[Kids 设计指南](https://developer.apple.com/kids/)、[年龄分级定义](https://developer.apple.com/help/app-store-connect/reference/age-ratings)、[截图规格](https://developer.apple.com/help/app-store-connect/reference/screenshot-specifications)、[TestFlight 概览](https://developer.apple.com/help/app-store-connect/test-a-beta-version/overview-of-testflight/)、[TestFlight 条款（13 岁以下不能用）](https://www.apple.com/legal/internet-services/testflight/)、[SDK 最低要求](https://developer.apple.com/news/upcoming-requirements/)
