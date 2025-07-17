@echo off
chcp 65001 >nul
title 重复文件清理工具 - GUI版本（简化版）

echo ========================================
echo 重复文件清理工具 - GUI版本（简化版）
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python环境
    echo 请先安装Python 3.6或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [信息] 正在启动GUI程序...
echo.

:: 启动GUI程序
python "%~dp0duplicate_finder_gui_simple.py"

if errorlevel 1 (
    echo.
    echo [错误] 程序运行出错
    echo 可能的原因：
    echo 1. tkinter模块未安装（通常随Python一起安装）
    echo 2. Python版本过低（需要3.6+）
    echo 3. 文件权限问题
    echo.
    echo 如果问题持续存在，请尝试：
    echo 1. 重新安装Python并确保勾选"Add Python to PATH"
    echo 2. 使用管理员权限运行此脚本
    echo.
    pause
    exit /b 1
)

echo.
echo [信息] 程序已退出
pause