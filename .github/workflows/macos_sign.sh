#!/bin/bash

# macOS签名脚本
# 用于在GitHub Actions中对macOS应用进行签名

# 设置变量
APP_NAME="crypto_wallet_secure"
DIST_DIR="dist"

echo "===== macOS应用签名 ====="

# 检查是否在macOS环境中运行
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "错误: 此脚本只能在macOS环境中运行"
    exit 1
fi

# 创建Info.plist文件
cat > "$DIST_DIR/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDisplayName</key>
    <string>加密货币钱包助记词生成工具</string>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
    <key>CFBundleIconFile</key>
    <string>AppIcon</string>
    <key>CFBundleIdentifier</key>
    <string>com.cryptowallet.generator</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>加密货币钱包助记词生成工具</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>1.3.2</string>
    <key>NSHighResolutionCapable</key>
    <true/>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
</dict>
</plist>
EOF

echo "创建了Info.plist文件"

# 移除所有文件的quarantine属性
find "$DIST_DIR" -type f -exec xattr -d com.apple.quarantine {} \; 2>/dev/null || true
echo "移除了quarantine属性"

# 设置可执行权限
chmod +x "$DIST_DIR/$APP_NAME"
chmod +x "$DIST_DIR/启动钱包生成工具.command"
echo "设置了可执行权限"

echo "===== macOS应用签名完成 ====="
exit 0