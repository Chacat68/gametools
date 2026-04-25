param(
    [string]$ExePath,
    [int]$TimeoutSeconds = 30,
    [switch]$KeepRunning
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-TargetExe {
    param([string]$RequestedPath)

    if ($RequestedPath) {
        return (Resolve-Path -LiteralPath $RequestedPath).Path
    }

    $distDir = Join-Path $PSScriptRoot 'dist'
    $latestExe = Get-ChildItem -Path $distDir -Filter 'gametools_v*.exe' -File |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if (-not $latestExe) {
        throw "未在 $distDir 下找到 gametools_v*.exe"
    }

    return $latestExe.FullName
}

function Get-MatchingProcesses {
    param(
        [string]$ResolvedExePath,
        [string]$ProcessName
    )

    Get-Process -Name $ProcessName -ErrorAction SilentlyContinue |
        Where-Object {
            try {
                $_.Path -and ([System.StringComparer]::OrdinalIgnoreCase.Equals($_.Path, $ResolvedExePath))
            } catch {
                $false
            }
        }
}

$resolvedExePath = Resolve-TargetExe -RequestedPath $ExePath
$processName = [System.IO.Path]::GetFileNameWithoutExtension($resolvedExePath)
$existingProcessIds = @(
    Get-MatchingProcesses -ResolvedExePath $resolvedExePath -ProcessName $processName |
        Select-Object -ExpandProperty Id
)

Write-Output "[INFO] Exe: $resolvedExePath"
Write-Output "[INFO] ProcessName: $processName"
Write-Output "[INFO] TimeoutSeconds: $TimeoutSeconds"

$startedProc = Start-Process -FilePath $resolvedExePath -PassThru
Write-Output "[INFO] Initial PID: $($startedProc.Id)"

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$windowProcess = $null

while ((Get-Date) -lt $deadline) {
    $matchingProcesses = @(
        Get-MatchingProcesses -ResolvedExePath $resolvedExePath -ProcessName $processName |
            Where-Object { $_.Id -notin $existingProcessIds }
    )

    if (-not $matchingProcesses -and $startedProc.HasExited) {
        throw "进程已退出，且未发现同名驻留进程。初始 ExitCode=$($startedProc.ExitCode)"
    }

    $windowProcess = $matchingProcesses | Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
    if ($windowProcess) {
        break
    }

    Start-Sleep -Milliseconds 500
}

if (-not $windowProcess) {
    $matchingProcesses = @(
        Get-MatchingProcesses -ResolvedExePath $resolvedExePath -ProcessName $processName |
            Where-Object { $_.Id -notin $existingProcessIds }
    )
    if ($matchingProcesses) {
        Write-Output "[INFO] 当前匹配进程:"
        $matchingProcesses |
            Select-Object Id, ProcessName, MainWindowHandle, MainWindowTitle, Responding, Path |
            Format-List |
            Out-String |
            Write-Output
    }
    throw "在 $TimeoutSeconds 秒内未发现主窗口句柄"
}

Write-Output "[SUCCESS] 主窗口已出现"
Write-Output "[INFO] Window PID: $($windowProcess.Id)"
Write-Output "[INFO] Window Title: $($windowProcess.MainWindowTitle)"

if (-not $KeepRunning) {
    $allProcesses = @(
        Get-MatchingProcesses -ResolvedExePath $resolvedExePath -ProcessName $processName |
            Where-Object { $_.Id -notin $existingProcessIds }
    )
    foreach ($proc in $allProcesses) {
        Write-Output "[INFO] Stopping PID: $($proc.Id)"
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
}
