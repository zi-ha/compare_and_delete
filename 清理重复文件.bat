@echo off
chcp 65001 >nul
echo ========================================
echo 文件夹重复文件清理工具
echo ========================================
echo.

if "%~2"=="" (
    echo 使用方法: %~nx0 源文件夹路径 目标文件夹路径 [选项]
    echo.
    echo 参数说明:
    echo   源文件夹路径    - 参考文件夹，不会删除其中的文件
    echo   目标文件夹路径  - 要清理重复文件的文件夹
    echo.
    echo 选项:
    echo   --execute      - 实际执行删除操作（默认为试运行）
    echo   --sha256       - 使用SHA256算法（默认为MD5）
    echo.
    echo 示例:
    echo   %~nx0 "C:\原始文件夹" "C:\备份文件夹"
    echo   %~nx0 "C:\原始文件夹" "C:\备份文件夹" --execute
    echo   %~nx0 "C:\原始文件夹" "C:\备份文件夹" --execute --sha256
    echo.
    pause
    exit /b 1
)

set "SOURCE_FOLDER=%~1"
set "TARGET_FOLDER=%~2"
set "ALGORITHM=md5"
set "DRY_RUN=--dry-run"

:parse_args
if "%~3"=="" goto :run_script
if /i "%~3"=="--execute" (
    set "DRY_RUN="
    shift
    goto :parse_args
)
if /i "%~3"=="--sha256" (
    set "ALGORITHM=sha256"
    shift
    goto :parse_args
)
shift
goto :parse_args

:run_script
echo 正在检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python环境，请先安装Python
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo.
echo 开始执行文件比较...
if "%DRY_RUN%"=="" (
    python "%~dp0compare_and_delete_duplicates.py" "%SOURCE_FOLDER%" "%TARGET_FOLDER%" --algorithm %ALGORITHM% --execute
) else (
    python "%~dp0compare_and_delete_duplicates.py" "%SOURCE_FOLDER%" "%TARGET_FOLDER%" --algorithm %ALGORITHM%
)

echo.
echo 操作完成，按任意键退出...
pause >nul