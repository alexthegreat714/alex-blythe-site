@echo off
setlocal EnableExtensions

set "PROJECT_DIR=%~dp0"
set "CODEX_DEPS=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies"

if exist "%CODEX_DEPS%\node\bin\node.exe" if exist "%CODEX_DEPS%\bin\fallback\pnpm.cmd" (
  set "PATH=%CODEX_DEPS%\node\bin;%CODEX_DEPS%\bin\fallback;%PATH%"
  set "PNPM_COMMAND=%CODEX_DEPS%\bin\fallback\pnpm.cmd"
)

if not defined PNPM_COMMAND (
  "%SystemRoot%\System32\where.exe" node >nul 2>nul
  if errorlevel 1 (
    echo Node.js was not found.
    echo Install Node.js 22.12 or newer, or run this project from Codex Desktop.
    exit /b 1
  )

  "%SystemRoot%\System32\where.exe" pnpm >nul 2>nul
  if errorlevel 1 (
    echo pnpm was not found.
    echo Install it with: npm install --global pnpm
    exit /b 1
  )
  set "PNPM_COMMAND=pnpm"
)

if "%~1"=="" (
  echo Usage: .\site.cmd install ^| dev ^| build ^| preview
  exit /b 1
)

pushd "%PROJECT_DIR%"
call "%PNPM_COMMAND%" %*
set "SITE_EXIT_CODE=%ERRORLEVEL%"
popd

exit /b %SITE_EXIT_CODE%
