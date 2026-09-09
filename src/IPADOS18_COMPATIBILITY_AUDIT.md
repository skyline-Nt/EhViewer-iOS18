# iPadOS 18 兼容性初步检查

日期：2026-09-08。对象：D:/pt/EhViewer-Apple-main 本地源码快照（135 个 Swift 文件）。目录无 .git，无法证明与远程 main 或 v1.3.1 完全一致；正式实施应记录源码来源及提交版本。本次仅做静态检查，未修改应用代码，也未进行 Xcode 编译或实机测试。

## 结论

值得进行 iOS 18 编译试验。已确认的主要阻碍是主应用与测试目标的最低系统配置，以及现有发布流程。检索未发现直接使用 glassEffect、GlassEffectContainer、BGContinuedProcessingTask 等 iOS 26 专用 API 的证据；这不是完整的 SDK 可用性证明，不能代替编译。

目前没有证据支持必须大规模重写阅读、网络或下载模块。建议先降低部署目标并使用现代 Xcode 编译，按照真实编译错误逐项修复，而不是预先降级 Swift 或删除功能。

## 源码证据

| 项目 | 位置 | 结果及处理 |
|---|---|---|
| 主应用最低系统 | ehviewer apple.xcodeproj/project.pbxproj:460、506 | Debug/Release 均为 26.2，需改为 18.0 |
| 测试最低系统 | 同文件：651、677、702、727 | 单元测试和 UI 测试也需改为 18.0 |
| 下载扩展 | 同文件：756、787 | 已为 18.0，无需降低 |
| 内部模块 | Packages 下六个 Package.swift:7 | EhCore、EhNetwork、EhParser、EhSpider、EhDownload、EhUI 均声明 iOS 17 |
| 玻璃效果 | ehviewer apple/DesignSystem/EhMetrics.swift:135 起 | ultraThinMaterial、颜色叠层、圆角和描边，不是 iOS 26 的 glassEffect |
| 滚动监听 | ehviewer apple/DesignSystem/EhFloatingTabBar.swift:152 | onScrollGeometryChange 属于 iOS 18 时代的 API，应保留 |
| 阅读器 | ehviewer apple/ImageReaderView.swift:664、697、867 | 使用 scrollPosition(id:)；不因这一调用要求 iOS 26 |
| 后台下载 | ehviewer apple/BackgroundDownloadManager.swift:21、70、86 | background URLSession、BGProcessingTaskRequest、BGAppRefreshTaskRequest；未发现依赖 BGContinuedProcessingTask |
| 后台时间申请 | Packages/EhDownload/Sources/EhDownload/DownloadManager.swift:358 起 | 使用 UIApplication.beginBackgroundTask；锁屏长期下载仍需实机验证，不能保证无限后台运行 |
| Swift 配置 | project.pbxproj:471–475 | 新工具链并发设置与 SWIFT_VERSION=5.0 并存；内部包工具版本为 6.0。工具链要求与设备最低系统应分开处理 |
| 自动更新 | ehviewer apple/AppUpdateChecker.swift:67 | 固定查询原作者 releases/latest；兼容分支需改为自己的发布源或暂时禁用原版升级提示 |

## 外部依赖

以工程 workspace 的 Package.resolved 为准：GRDB 7.9.0、SwiftSoup 2.11.3、SDWebImageSwiftUI 3.1.4、SDWebImage 5.21.6、LRUCache 1.2.1、swift-atomics 1.3.0。

已核对主要直接依赖官方 manifest：

- [GRDB 7.9.0](https://raw.githubusercontent.com/groue/GRDB.swift/v7.9.0/Package.swift)：iOS 13 起，但编译需要 Swift 6.1。
- [SwiftSoup 2.11.3](https://raw.githubusercontent.com/scinfu/SwiftSoup/2.11.3/Package.swift)：iOS 13 起，Swift 工具版本 6.0。
- [SDWebImageSwiftUI 3.1.4](https://raw.githubusercontent.com/SDWebImage/SDWebImageSwiftUI/3.1.4/Package.swift)：iOS 14 起。

没有从这些最低系统声明看到 iOS 18 障碍。间接依赖未逐源码审计，所有依赖仍须实际解析、编译及链接；首次试验应保持锁定版本，避免更新依赖扩大变量。

Apple 的 [WWDC24 SwiftUI 介绍](https://developer.apple.com/videos/play/wwdc2024/10144/)介绍了新的滚动监听；[Observation 文档](https://developer.apple.com/documentation/SwiftUI/Managing-model-data-in-your-app)明确其从 iOS 17 起支持。README 将此类功能归为必须 iOS 26 的理由不充分。

## 无 Mac 的实施方式

现有 .github/workflows/build.yml 已使用 macOS runner 无签名构建 iOS，但不产出 IPA，也不运行 iOS 18 测试。deploy_ios.yml 则依赖证书、App Store Connect 密钥及作者 Team ID，并包含发布/服务器部署步骤，不能直接作为个人兼容构建使用。

建议新增独立、手动触发的兼容构建：

1. 使用明确的 Xcode 26.x 环境，保持现代编译器；主应用和测试目标设为 iOS 18.0。
2. 解析锁定依赖，构建 arm64 真机 Release，禁用签名。
3. 将归档中的应用和扩展按 Payload/*.app 打包为待重签 IPA，通过 Actions artifact 下载；不要求 Apple 密码、证书或发布到外部服务器。
4. 校验应用、扩展和嵌入框架的最低系统及二进制链接信息，确保没有高于目标系统的硬性要求。
5. 配置可用的 iOS 18 模拟器运行环境，执行已有测试及启动检查；仅以 iOS 18 部署目标编译不等于在 iOS 18 上运行测试。
6. 用户在 Windows 侧载工具中自行签名，在 iPadOS 18 设备测试。

当前 entitlements 文件还含 Keychain access group 及 macOS 权限，与 README 的简化描述有差异。打包时应按平台核对权限，重签后验证凭据保存、重启登录状态及下载扩展，不应直接删除 Keychain 权限。

## 实机验收

- 冷启动、登录、退出重开后的凭据保存。
- 首页、搜索、详情、收藏同步和分页。
- 横竖屏、分屏、双页排版、缩放、快速跳页、GIF。
- 下载、切换后台、锁屏、网络中断及恢复、离线阅读与导出。
- 照片保存、通知、设备支持的认证方式及 Live Activity。
- 更新入口不会提供仅支持 iOS 26 的原版作为兼容升级。

本次交付是兼容性分析，不是已验证 IPA。下一阶段应先做最小配置改动和一次云端编译；若通过，才有依据把预估收敛为少量适配。
