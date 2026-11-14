// Native side of the Drawrassic Park app. JS side: apps/ios/shell/app-shell.js (window.FamilyNative).
//
// MainViewController  – Capacitor's view controller plus app-like defaults (no status bar,
//                       no back/forward swipe, edge swipes go to the game first).
// FamilyNativePlugin  – Game Center, haptics, iCloud saves, save image to Photos, clipboard,
//                       and a navigation guard so nothing can leave the app.
//
// Every method resolves (never rejects) with ["ok": Bool, ...] so the game can feature-detect.
// Game Center and iCloud need the capability added in Xcode (see apps/ios/README.md); until then
// they answer ok:false, reason:"unavailable" and nothing else changes.

import UIKit
import WebKit
import Capacitor
import GameKit
import Photos

class MainViewController: CAPBridgeViewController {
    override func capacitorDidLoad() {
        bridge?.registerPluginInstance(FamilyNativePlugin())
        webView?.allowsBackForwardNavigationGestures = false
        webView?.scrollView.bounces = false
        webView?.scrollView.contentInsetAdjustmentBehavior = .never
    }

    override var prefersStatusBarHidden: Bool { true }
    override var prefersHomeIndicatorAutoHidden: Bool { true }
    // Swipes that start at a screen edge reach the game first; a second swipe still opens
    // Control Center / the Home Screen.
    override var preferredScreenEdgesDeferringSystemGestures: UIRectEdge { .all }
}

@objc(FamilyNativePlugin)
public class FamilyNativePlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "FamilyNativePlugin"
    public let jsName = "FamilyNative"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "info", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "haptic", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "gcSignIn", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "gcSubmitScore", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "gcReportAchievement", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "gcShowDashboard", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "cloudStatus", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "cloudSave", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "cloudLoad", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "cloudList", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "saveImage", returnType: CAPPluginReturnPromise),
        CAPPluginMethod(name: "copyText", returnType: CAPPluginReturnPromise)
    ]

    private func okWith(_ extra: [String: Any]) -> [String: Any] {
        var r: [String: Any] = ["ok": true]
        extra.forEach { r[$0.key] = $0.value }
        return r
    }

    private func fail(_ call: CAPPluginCall, _ reason: String, _ extra: [String: Any] = [:]) {
        var r: [String: Any] = ["ok": false, "reason": reason]
        extra.forEach { r[$0.key] = $0.value }
        call.resolve(r)
    }

    // MARK: - No links out of the app
    // Anything that isn't the app's own page (http, https, mailto, tel, itms-apps, …) is cancelled
    // instead of being handed to Safari or another app. Network requests (fetch, WebSocket) are not
    // navigations and are not affected.
    override public func shouldOverrideLoad(_ navigationAction: WKNavigationAction) -> NSNumber? {
        guard let scheme = navigationAction.request.url?.scheme?.lowercased() else { return nil }
        if ["capacitor", "about", "data", "blob"].contains(scheme) { return nil }
        return true
    }

    // MARK: - Info
    @objc func info(_ call: CAPPluginCall) {
        DispatchQueue.main.async {
            let b = Bundle.main.infoDictionary ?? [:]
            var r: [String: Any] = [
                "ok": true,
                "appVersion": b["CFBundleShortVersionString"] as? String ?? "",
                "build": b["CFBundleVersion"] as? String ?? "",
                "iCloudSignedIn": FileManager.default.ubiquityIdentityToken != nil
            ]
            r.merge(self.gcState()) { $1 }
            call.resolve(r)
        }
    }

    // MARK: - Haptics
    @objc func haptic(_ call: CAPPluginCall) {
        let style = call.getString("style") ?? "medium"
        DispatchQueue.main.async {
            switch style {
            case "success": UINotificationFeedbackGenerator().notificationOccurred(.success)
            case "warning": UINotificationFeedbackGenerator().notificationOccurred(.warning)
            case "error": UINotificationFeedbackGenerator().notificationOccurred(.error)
            case "selection": UISelectionFeedbackGenerator().selectionChanged()
            case "light": UIImpactFeedbackGenerator(style: .light).impactOccurred()
            case "heavy": UIImpactFeedbackGenerator(style: .heavy).impactOccurred()
            case "soft": UIImpactFeedbackGenerator(style: .soft).impactOccurred()
            case "rigid": UIImpactFeedbackGenerator(style: .rigid).impactOccurred()
            default: UIImpactFeedbackGenerator(style: .medium).impactOccurred()
            }
            call.resolve(["ok": true])
        }
    }

    // MARK: - Game Center
    private func gcState() -> [String: Any] {
        let p = GKLocalPlayer.local
        var r: [String: Any] = ["gameCenter": p.isAuthenticated]
        if p.isAuthenticated {
            r["underage"] = p.isUnderage
            r["multiplayerRestricted"] = p.isMultiplayerGamingRestricted
            r["communicationRestricted"] = p.isPersonalizedCommunicationRestricted
        }
        return r
    }
    private var gcPending: [CAPPluginCall] = []
    private var gcHandlerSet = false

    @objc func gcSignIn(_ call: CAPPluginCall) {
        DispatchQueue.main.async {
            let p = GKLocalPlayer.local
            if p.isAuthenticated { call.resolve(self.okWith(self.gcState())); return }
            self.gcPending.append(call)
            if self.gcHandlerSet { return }   // iOS calls the handler again whenever the state changes
            self.gcHandlerSet = true
            p.authenticateHandler = { [weak self] vc, error in
                guard let self = self else { return }
                if let vc = vc { self.bridge?.viewController?.present(vc, animated: true); return }
                let calls = self.gcPending; self.gcPending = []
                for c in calls {
                    if p.isAuthenticated { c.resolve(self.okWith(self.gcState())) }
                    else { self.fail(c, (error as NSError?).map { "gc-\($0.code)" } ?? "not-signed-in") }
                }
            }
        }
    }

    @objc func gcSubmitScore(_ call: CAPPluginCall) {
        guard let board = call.getString("leaderboardId"), !board.isEmpty else { return fail(call, "missing-leaderboardId") }
        let score = call.getInt("score") ?? 0
        guard GKLocalPlayer.local.isAuthenticated else { return fail(call, "not-signed-in") }
        GKLeaderboard.submitScore(score, context: 0, player: GKLocalPlayer.local, leaderboardIDs: [board]) { error in
            if let e = error { self.fail(call, e.localizedDescription) } else { call.resolve(["ok": true]) }
        }
    }

    @objc func gcReportAchievement(_ call: CAPPluginCall) {
        guard let id = call.getString("achievementId"), !id.isEmpty else { return fail(call, "missing-achievementId") }
        guard GKLocalPlayer.local.isAuthenticated else { return fail(call, "not-signed-in") }
        let a = GKAchievement(identifier: id)
        a.percentComplete = max(0, min(100, call.getDouble("percent") ?? 100))
        a.showsCompletionBanner = true
        GKAchievement.report([a]) { error in
            if let e = error { self.fail(call, e.localizedDescription) } else { call.resolve(["ok": true]) }
        }
    }

    @objc func gcShowDashboard(_ call: CAPPluginCall) {
        DispatchQueue.main.async {
            guard GKLocalPlayer.local.isAuthenticated else { return self.fail(call, "not-signed-in") }
            let state: GKGameCenterViewControllerState
            switch call.getString("state") ?? "default" {
            case "leaderboards": state = .leaderboards
            case "achievements": state = .achievements
            default: state = .dashboard
            }
            GKAccessPoint.shared.trigger(state: state) {}
            call.resolve(["ok": true])
        }
    }

    // MARK: - iCloud saves (iCloud Drive, this app's own container)
    // Files: <container>/Documents/<key>.json, previous copy kept as <key>.bak.json.
    private let cloudQueue = DispatchQueue(label: "family.native.cloud")
    private let keyPattern = try! NSRegularExpression(pattern: "^[a-z0-9._-]{1,64}$")
    private let maxBytes = 40 * 1024 * 1024

    private func validKey(_ k: String?) -> String? {
        guard let k = k, keyPattern.firstMatch(in: k, range: NSRange(k.startIndex..., in: k)) != nil,
              !k.hasSuffix(".bak") else { return nil }
        return k
    }
    private func cloudDocs() -> URL? {   // must not run on the main thread
        guard FileManager.default.ubiquityIdentityToken != nil,
              let root = FileManager.default.url(forUbiquityContainerIdentifier: nil) else { return nil }
        let docs = root.appendingPathComponent("Documents", isDirectory: true)
        try? FileManager.default.createDirectory(at: docs, withIntermediateDirectories: true)
        return docs
    }

    @objc func cloudStatus(_ call: CAPPluginCall) {
        cloudQueue.async {
            let signedIn = FileManager.default.ubiquityIdentityToken != nil
            let docs = self.cloudDocs()
            call.resolve(["ok": docs != nil, "signedIn": signedIn, "container": docs != nil,
                          "reason": docs != nil ? "" : (signedIn ? "no-container" : "not-signed-in")])
        }
    }

    @objc func cloudSave(_ call: CAPPluginCall) {
        guard let key = validKey(call.getString("key")) else { return fail(call, "bad-key") }
        guard let text = call.getString("data") else { return fail(call, "missing-data") }
        cloudQueue.async {
            guard let docs = self.cloudDocs() else { return self.fail(call, "unavailable") }
            let savedAt = Int(Date().timeIntervalSince1970 * 1000)
            let payload: [String: Any] = ["key": key, "savedAt": savedAt, "data": text,
                                          "app": Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? ""]
            guard let body = try? JSONSerialization.data(withJSONObject: payload), body.count <= self.maxBytes else {
                return self.fail(call, "too-big")
            }
            let file = docs.appendingPathComponent(key + ".json"), bak = docs.appendingPathComponent(key + ".bak.json")
            var coordErr: NSError?, writeErr: Error?
            NSFileCoordinator().coordinate(writingItemAt: file, options: .forReplacing, error: &coordErr) { url in
                do {
                    if let old = try? Data(contentsOf: url), (try? JSONSerialization.jsonObject(with: old)) != nil {
                        try old.write(to: bak, options: .atomic)      // keep the last good copy
                    }
                    try body.write(to: url, options: .atomic)
                } catch { writeErr = error }
            }
            if let e = coordErr ?? writeErr { self.fail(call, e.localizedDescription) }
            else { call.resolve(["ok": true, "savedAt": savedAt, "bytes": body.count]) }
        }
    }

    @objc func cloudLoad(_ call: CAPPluginCall) {
        guard let key = validKey(call.getString("key")) else { return fail(call, "bad-key") }
        cloudQueue.async {
            guard let docs = self.cloudDocs() else { return self.fail(call, "unavailable") }
            for (name, isBackup) in [(key + ".json", false), (key + ".bak.json", true)] {
                let url = docs.appendingPathComponent(name)
                let placeholder = docs.appendingPathComponent("." + name + ".icloud")
                let fm = FileManager.default
                if !fm.fileExists(atPath: url.path) && fm.fileExists(atPath: placeholder.path) {
                    try? fm.startDownloadingUbiquitousItem(at: url)
                    for _ in 0..<20 where !fm.fileExists(atPath: url.path) { Thread.sleep(forTimeInterval: 0.5) }
                    if !fm.fileExists(atPath: url.path) { return self.fail(call, "downloading") }
                }
                guard fm.fileExists(atPath: url.path) else { continue }
                var data: Data?
                var err: NSError?
                NSFileCoordinator().coordinate(readingItemAt: url, options: [], error: &err) { u in data = try? Data(contentsOf: u) }
                if let d = data, let obj = try? JSONSerialization.jsonObject(with: d) as? [String: Any],
                   let text = obj["data"] as? String {
                    return call.resolve(["ok": true, "data": text, "savedAt": obj["savedAt"] ?? 0, "fromBackup": isBackup])
                }
            }
            self.fail(call, "not-found")
        }
    }

    @objc func cloudList(_ call: CAPPluginCall) {
        cloudQueue.async {
            guard let docs = self.cloudDocs() else { return self.fail(call, "unavailable") }
            let names = (try? FileManager.default.contentsOfDirectory(atPath: docs.path)) ?? []
            var keys = Set<String>()
            for n in names {
                var s = n
                if s.hasPrefix(".") && s.hasSuffix(".icloud") { s = String(s.dropFirst().dropLast(7)) }
                if s.hasSuffix(".json") && !s.hasSuffix(".bak.json") { keys.insert(String(s.dropLast(5))) }
            }
            call.resolve(["ok": true, "keys": keys.sorted()])
        }
    }

    // MARK: - Save image to Photos (add-only permission)
    @objc func saveImage(_ call: CAPPluginCall) {
        guard let dataUrl = call.getString("dataUrl"), dataUrl.hasPrefix("data:image/"),
              let comma = dataUrl.firstIndex(of: ","),
              let data = Data(base64Encoded: String(dataUrl[dataUrl.index(after: comma)...]), options: .ignoreUnknownCharacters),
              UIImage(data: data) != nil else { return fail(call, "bad-image") }
        PHPhotoLibrary.requestAuthorization(for: .addOnly) { status in
            guard status == .authorized || status == .limited else { return self.fail(call, "denied") }
            PHPhotoLibrary.shared().performChanges({
                PHAssetCreationRequest.forAsset().addResource(with: .photo, data: data, options: nil)
            }) { ok, error in
                if ok { call.resolve(["ok": true]) } else { self.fail(call, error?.localizedDescription ?? "failed") }
            }
        }
    }

    // MARK: - Clipboard (fallback when WebKit refuses navigator.clipboard)
    @objc func copyText(_ call: CAPPluginCall) {
        let text = call.getString("text") ?? ""
        DispatchQueue.main.async {
            UIPasteboard.general.string = text
            call.resolve(["ok": true])
        }
    }
}
