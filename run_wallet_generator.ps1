# 加密货币钱包助记词生成工具 - PowerShell启动脚本
# 版本: 1.0.0

# 设置终端颜色
$GREEN = @{ForegroundColor = "Green"}
$BLUE = @{ForegroundColor = "Cyan"}
$YELLOW = @{ForegroundColor = "Yellow"}
$RED = @{ForegroundColor = "Red"}

# 清屏
Clear-Host

# 显示欢迎信息
Write-Host "================================================" @GREEN
Write-Host "    加密货币钱包助记词生成工具 - Windows版    " @GREEN
Write-Host "================================================" @GREEN
Write-Host "版本: 1.0.0" @BLUE
Write-Host ""
Write-Host "该工具可以帮助您生成符合BIP-39标准的加密货币钱包助记词" @BLUE
Write-Host ""

# 检查Python是否安装
function Check-Python {
    try {
        $pythonVersion = (python --version 2>&1)
        if ($pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)") {
            $major = [int]$Matches[1]
            $minor = [int]$Matches[2]
            
            if ($major -lt 3 -or ($major -eq 3 -and $minor -lt 7)) {
                Write-Host "警告: 检测到Python版本 $pythonVersion" @RED
                Write-Host "此工具需要Python 3.7或更高版本。" @RED
                $continue = Read-Host "是否继续? (y/n)"
                if ($continue -ne "y") {
                    exit
                }
            } else {
                Write-Host "检测到Python版本 $pythonVersion" @GREEN
            }
            return $true
        } else {
            throw "无法识别Python版本"
        }
    } catch {
        Write-Host "错误: 未找到Python。请先安装Python后再运行此脚本。" @RED
        Write-Host "您可以从 https://www.python.org/downloads/ 下载并安装Python。"
        Write-Host ""
        Write-Host "按任意键退出..." @YELLOW
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit
    }
}

# 检查系统环境
function Check-System {
    Write-Host "正在检查系统环境..." @BLUE
    
    # 检查操作系统版本
    $osVersion = [System.Environment]::OSVersion.Version
    $osName = "未知Windows版本"
    
    if ($osVersion.Major -eq 5) {
        $osName = "Windows XP"
        Write-Host "警告: 检测到$osName。此工具可能无法在Windows XP上正常运行。" @RED
        Write-Host "建议使用Windows 7或更高版本。" @YELLOW
    } elseif ($osVersion.Major -eq 6 -and $osVersion.Minor -eq 0) {
        $osName = "Windows Vista"
        Write-Host "检测到$osName。某些功能可能受限。" @YELLOW
    } elseif ($osVersion.Major -eq 6 -and $osVersion.Minor -eq 1) {
        $osName = "Windows 7"
        Write-Host "检测到$osName。" @GREEN
    } elseif ($osVersion.Major -eq 6 -and ($osVersion.Minor -eq 2 -or $osVersion.Minor -eq 3)) {
        $osName = "Windows 8/8.1"
        Write-Host "检测到$osName。" @GREEN
    } elseif ($osVersion.Major -eq 10) {
        if ($osVersion.Build -ge 22000) {
            $osName = "Windows 11"
        } else {
            $osName = "Windows 10"
        }
        Write-Host "检测到$osName。" @GREEN
    }
    
    # 检查PowerShell版本
    $psVersion = $PSVersionTable.PSVersion
    Write-Host "PowerShell版本: $psVersion" @GREEN
    
    # 检查.NET版本
    $dotNetVersion = [System.Runtime.InteropServices.RuntimeEnvironment]::GetSystemVersion()
    Write-Host ".NET版本: $dotNetVersion" @GREEN
}

# 安装依赖
function Install-Dependencies {
    param (
        [string]$reqFile
    )
    
    Write-Host "正在检查依赖库..." @BLUE
    
    # 尝试使用依赖管理器
    try {
        $pythonCmd = "import sys, os; sys.path.insert(0, os.getcwd()); from utils.dependency_manager import 依赖管理器; print('DEPENDENCY_MANAGER_AVAILABLE')"
        $result = python -c $pythonCmd 2>$null
        
        if ($result -eq "DEPENDENCY_MANAGER_AVAILABLE") {
            Write-Host "使用依赖管理器检查依赖..." @GREEN
            
            # 显示依赖状态
            $statusCmd = "import sys, os; sys.path.insert(0, os.getcwd()); from utils.dependency_manager import 依赖管理器; print(依赖管理器.显示依赖状态())"
            $status = python -c $statusCmd
            Write-Host $status
            
            # 询问是否安装缺失依赖
            $installDeps = Read-Host "是否自动安装缺失的依赖? (y/n)"
            
            if ($installDeps -eq "y") {
                Write-Host "正在安装依赖..." @BLUE
                
                # 安装依赖
                if ($reqFile -eq "requirements.txt") {
                    $installCmd = "import sys, os; sys.path.insert(0, os.getcwd()); from utils.dependency_manager import 依赖管理器; 依赖管理器.安装所有基础依赖()"
                    python -c $installCmd
                } elseif ($reqFile -eq "requirements_secure.txt") {
                    $installCmd = "import sys, os; sys.path.insert(0, os.getcwd()); from utils.dependency_manager import 依赖管理器; 依赖管理器.安装所有依赖()"
                    python -c $installCmd
                } else {
                    $installCmd = "import sys, os; sys.path.insert(0, os.getcwd()); from utils.dependency_manager import 依赖管理器; 依赖管理器.从文件安装依赖('$reqFile')"
                    python -c $installCmd
                }
                
                Write-Host "依赖安装完成！" @GREEN
            } else {
                Write-Host "警告: 缺少必要的依赖库，程序可能无法正常运行。" @RED
                Write-Host "按任意键继续..." @YELLOW
                $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            }
        } else {
            throw "依赖管理器不可用"
        }
    } catch {
        # 回退到传统方式检查依赖
        Write-Host "依赖管理器不可用，使用传统方式检查依赖..." @YELLOW
        
        $missingDeps = $false
        
        # 读取依赖文件中的每一行
        foreach ($line in Get-Content $reqFile) {
            if ($line -match "^([^=><]+)") {
                $package = $Matches[1].Trim()
                
                try {
                    $null = python -c "import $package"
                } catch {
                    Write-Host "未安装: $package" @YELLOW
                    $missingDeps = $true
                }
            }
        }
        
        # 如果有缺失的依赖，提示安装
        if ($missingDeps) {
            Write-Host ""
            Write-Host "检测到缺少依赖库。是否要自动安装？(y/n)" @YELLOW
            $installMissing = Read-Host
            
            if ($installMissing -eq "y") {
                Write-Host "正在安装依赖..." @BLUE
                pip install --no-warn-script-location -r $reqFile
                Write-Host "依赖安装完成！" @GREEN
            } else {
                Write-Host "警告: 缺少必要的依赖库，程序可能无法正常运行。" @RED
            }
        } else {
            Write-Host "所有依赖已安装。" @GREEN
        }
    }
}

# 主菜单
function Show-Menu {
    Write-Host ""
    Write-Host "请选择要使用的版本:" @BLUE
    Write-Host ""
    Write-Host "1. 基础版本" @YELLOW -NoNewline
    Write-Host " - 简单的命令行工具，支持基本的助记词生成功能 " -NoNewline
    Write-Host "(建议只生成一次性钱包使用)" @RED
    Write-Host "2. 高安全标准版本" @YELLOW -NoNewline
    Write-Host " - 提供多源熵、内存安全处理、SLIP-39分割备份等高级安全特性"
    Write-Host "3. 安装依赖" @YELLOW -NoNewline
    Write-Host " - 安装运行工具所需的依赖库"
    Write-Host "4. 检查系统环境" @YELLOW -NoNewline
    Write-Host " - 检查系统环境并诊断问题"
    Write-Host "5. 退出" @YELLOW
    Write-Host "0. 帮助信息" @YELLOW
    Write-Host ""
    Write-Host "请输入选项 (0-5):" @BLUE
    
    $choice = Read-Host
    
    switch ($choice) {
        "0" {
            # 显示帮助信息
            Clear-Host
            Write-Host "================================================" @GREEN
            Write-Host "    加密货币钱包助记词生成工具 - 帮助信息    " @GREEN
            Write-Host "================================================" @GREEN
            Write-Host "版本: 1.0.0" @BLUE
            Write-Host ""
            Write-Host "该工具可以帮助您生成符合BIP-39标准的加密货币钱包助记词" @BLUE
            Write-Host ""
            Write-Host "使用说明:" @YELLOW
            Write-Host "1. 基础版本适合简单使用，生成标准BIP-39助记词"
            Write-Host "2. 高安全标准版本提供更多安全特性，推荐用于重要钱包"
            Write-Host "3. 首次使用请先安装依赖"
            Write-Host "4. 如遇问题，可使用系统环境检查功能诊断"
            Write-Host ""
            Write-Host "按任意键返回主菜单..." @YELLOW
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            Show-Menu
        }
        "1" {
            Install-Dependencies "requirements.txt"
            Write-Host "启动基础版本..." @GREEN
            Write-Host "提示: 使用 'python crypto_wallet_generator.py --help' 查看命令行参数" @YELLOW
            Write-Host ""
            python crypto_wallet_generator.py generate
            End-Program
        }
        "2" {
            Install-Dependencies "requirements_secure.txt"
            Write-Host "启动高安全标准版本..." @GREEN
            python crypto_wallet_secure_optimized.py
            End-Program
        }
        "3" {
            Write-Host "请选择要安装的依赖:" @BLUE
            Write-Host "1. 基础版本依赖" @YELLOW
            Write-Host "2. 高安全标准版本依赖" @YELLOW
            Write-Host "3. 全部依赖" @YELLOW
            Write-Host "4. 返回主菜单" @YELLOW
            Write-Host ""
            Write-Host "请输入选项 (1-4):" @BLUE
            
            $depChoice = Read-Host
            
            switch ($depChoice) {
                "1" {
                    pip install --no-warn-script-location -r requirements.txt
                    Write-Host "基础版本依赖安装完成！" @GREEN
                }
                "2" {
                    pip install --no-warn-script-location -r requirements_secure.txt
                    Write-Host "高安全标准版本依赖安装完成！" @GREEN
                }
                "3" {
                    pip install --no-warn-script-location -r requirements.txt
                    pip install --no-warn-script-location -r requirements_secure.txt
                    Write-Host "所有依赖安装完成！" @GREEN
                }
                "4" {
                    Show-Menu
                    return
                }
                default {
                    Write-Host "无效选项，请重新选择" @RED
                }
            }
            
            Write-Host "按任意键返回主菜单..." @YELLOW
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            Show-Menu
        }
        "4" {
            Check-System
            Write-Host "按回车键返回主菜单..." @YELLOW
            $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
            Show-Menu
        }
        "5" {
            Write-Host "感谢使用！再见！" @GREEN
            exit
        }
        default {
            Write-Host "无效选项，请重新选择" @RED
            Show-Menu
        }
    }
}

# 程序结束
function End-Program {
    Write-Host ""
    Write-Host "程序已结束。按任意键退出..." @GREEN
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit
}

# 主程序
function Main {
    # 检查Python
    Check-Python
    
    # 检查系统环境
    Check-System
    
    # 运行主菜单
    Show-Menu
}

# 执行主程序
Main