# EhViewer-iOS18 v1.0.1

基于 [felixchaos/EhViewer-Apple](https://github.com/felixchaos/EhViewer-Apple) 的 iOS / iPadOS 18 兼容移植。原项目的应用实现、界面与功能由上游作者及贡献者完成，本仓库主要提供兼容配置与 GitHub Actions 构建流程。

## 为什么移植

上游项目面向较新的 Apple 系统。本移植希望让仍使用 iOS / iPadOS 18 的设备也能运行 EhViewer，并通过 GitHub Actions 在云端构建 IPA，让没有 Mac、使用 Windows 的用户也能获取待签名的安装包。

## 当前版本与验证情况

维护者已反馈第一版可以安装运行，因此保留第一版 `EhViewer-iOS18-source.zip` 作为使用和构建基线。

第一版已有一次 [GitHub Actions 成功构建记录](https://github.com/skyline-Nt/EhViewer-iOS18/actions/runs/34223004001)，对应提交 `732d7c95e1171919f2764c18fe9a0dc36834d05b`。构建成功与维护者的运行反馈不代表全部设备或功能都已完成测试。

## 下载与安装

在 [v1.0.1 发布页](https://github.com/skyline-Nt/EhViewer-iOS18/releases/tag/v1.0.1) 下载 EhViewer-iOS18-unsigned.ipa。该 IPA 来自下面记录的第一版成功构建，未重新修改应用二进制，需要使用自己的账号重新签名后安装。发布页同时提供源码压缩包与构建兼容性报告。

v1.0.1 是本兼容仓库的发布版本；保留的第一版源码及应用内版本号没有改动。

## 自行构建

1. 打开本仓库的 [Actions](https://github.com/skyline-Nt/EhViewer-iOS18/actions/workflows/ios18-from-archive.yml)，选择 **iOS 18 IPA (source archive)**。
2. 点击 **Run workflow**，选择 `main` 并启动构建。工作流会解压第一版源码，使用 macOS runner 和 Xcode 26.2 构建最低系统版本为 iOS 18.0 的 IPA。
3. 构建成功后，在本次运行的 **Artifacts** 中下载 `EhViewer-iOS18-unsigned-运行编号`。
4. 解压 ZIP，取得 `EhViewer-iOS18-unsigned.ipa`。这是未签名安装包，需要在自己的设备安装流程中完成重新签名，不能直接点开安装。

### 维护者成功安装记录

已确认的结果：第一版可运行。

待维护者补充具体签名工具、设备系统版本和操作步骤后，再写入完整实测流程，避免把通用侧载步骤误写为个人实测。

上游的通用安装说明可参考 [安装与签名 Wiki](https://github.com/felixchaos/EhViewer-Apple/wiki/Installation)；其中的上游安装包不等同于本仓库的 iOS 18 兼容包。

## 源码与协议

第一版完整源码可直接在 [`src/`](src/) 中浏览，包含 Xcode 工程、Packages、原有文档及 LICENSE。该目录与 [`EhViewer-iOS18-source.zip`](EhViewer-iOS18-source.zip) 内容一致；现有构建工作流仍使用此源码压缩包。GitHub 右侧 Languages 根据实际源码自动统计。

保留上游 [Apache License 2.0](https://github.com/felixchaos/EhViewer-Apple/blob/main/LICENSE) 及源码中的版权声明；完整许可证也随源码压缩包提供。本仓库是独立兼容移植，不代表上游官方发行。

## 致谢

- [felixchaos/EhViewer-Apple](https://github.com/felixchaos/EhViewer-Apple)：本移植直接基于的源项目，感谢作者及所有贡献者的开发和开源。
- [EhViewer](https://github.com/Ehviewer-Overhauled/Ehviewer) 与 [EhViewer_CN_SXJ](https://github.com/xiaojieonly/Ehviewer_CN_SXJ)：感谢相关客户端及上游所参考的实现。
- [GRDB.swift](https://github.com/groue/GRDB.swift) 及其他依赖的维护者：感谢基础组件支持。

兼容移植相关问题请在本仓库反馈，并附设备系统版本、构建编号与复现步骤。
