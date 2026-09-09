# iOS / iPadOS 18 兼容构建

当前状态：已修改源码与构建配置；尚未在 macOS 编译，也未实机验证。不是已验证发行版。

## 本次修改

- 主应用、单元测试及 UI 测试的 Debug/Release 最低 iOS 版本统一为 18.0；下载扩展原本就是 18.0。
- 保留内部模块、阅读和下载功能，保留现代 Swift 编译器设置。
- iOS 兼容版不再自动查询上游更新；手动检查提示从兼容版来源获取更新，避免误装仅支持 iOS 26 的上游 IPA。
- 添加独立、手动触发的无签名 IPA 构建。上游证书发布流程在其他仓库自动跳过。

## 用 GitHub 编译

1. 将这个目录的完整内容上传到自己的 GitHub 仓库。仓库根目录应直接包含 `ehviewer apple.xcodeproj`、`Packages`、`.github`，不要额外套一层文件夹。必须包含隐藏目录 `.github` 和工程内的 `Package.resolved`。
2. 在仓库 Actions 页面按需要启用工作流。
3. 选择 **iOS 18 IPA (unsigned)**，点击 **Run workflow**，选择包含这些改动的分支并运行。
4. 构建成功后，在本次运行的 Artifacts 下载 `EhViewer-iOS18-unsigned-运行编号`。
5. 解压 artifact ZIP，得到 `EhViewer-iOS18-unsigned.ipa`、`compatibility.json` 和安装提示。
6. 在自己的 Windows 电脑上使用侧载工具重新签名 IPA，并安装到 iPad。Apple 账号由你在签名工具中自行登录，不需要放进 GitHub Secrets。

构建环境固定为 macos-15 / Xcode 26.2。现代 SDK 用于编译，部署目标为 iOS 18.0，这两者不同。若未来 runner 不再提供该 Xcode，工作流会明确失败，需要更新已验证的构建工具版本。

构建会使用工程锁定的依赖版本；若解析失败，应检查锁文件和依赖兼容性，不要直接更新全部依赖。

## 构建检查与局限

打包脚本要求归档只有一个主应用，检查主应用、扩展、框架的 MinimumOSVersion，并读取全部嵌入 Mach-O 文件的架构、平台和最低系统，拒绝高于 iOS 18.0 或非 iOS 平台的二进制，输出 SHA-256 和检查报告。

IPA **未签名**，不能直接点击安装。这些检查不代表 iOS 18 启动或功能测试已通过。当前工作流只做 Release 真机归档及元数据检查，不运行模拟器测试。

失败时下载 `iOS18-build-log-运行编号` 中的 archive.log / Archive.xcresult，使用真实编译错误继续修复。上传源码、启用工作流和云端运行尚未执行。

## 实机测试顺序

先测试启动、登录及重开后的登录状态，再测搜索、阅读、横竖屏、双页排版、缩放、下载与离线阅读，最后测试锁屏后台下载和通知。Keychain 与下载扩展也需在重新签名后验证。

原有 source.json 指向上游官方 IPA，不要把它当作兼容版安装源。待有自己的已验证发布包后，再建立兼容版更新源。
