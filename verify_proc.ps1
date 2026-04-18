$exePath = "dist\gametools_v1.46.46.exe"
$processName = "gametools_v1.46.46"
$altProcessName = "gametools"

Write-Output "--- Starting Process ---"
$initialProc = Start-Process -FilePath $exePath -PassThru
$initialPid = $initialProc.Id
Write-Output "Initial PID: $initialPid"

Start-Sleep -Seconds 3

Write-Output "--- Checking Process Status ---"
$initialRunning = Get-Process -Id $initialPid -ErrorAction SilentlyContinue

if ($null -eq $initialRunning) {
    Write-Output "Initial PID $initialPid has exited. Searching for child or related processes..."
} else {
    Write-Output "Initial PID $initialPid is still running."
}

$relatedProcs = Get-CimInstance Win32_Process -Filter "Name = '$processName.exe' OR Name = '$altProcessName.exe'" | 
                Select-Object ProcessId, ParentProcessId, CommandLine, CreationDate

if ($relatedProcs) {
    Write-Output "Found related processes:"
    foreach ($p in $relatedProcs) {
        $age = (Get-Date) - $p.CreationDate
        Write-Output "PID: $($p.ProcessId), ParentPID: $($p.ParentProcessId), Age: $($age.TotalSeconds)s, Cmd: $($p.CommandLine)"
    }
} else {
    Write-Output "No related processes found."
}

Write-Output "--- Waiting 10 seconds total for stability ---"
Start-Sleep -Seconds 7

$finalProcs = Get-CimInstance Win32_Process -Filter "Name = '$processName.exe' OR Name = '$altProcessName.exe'"
if ($finalProcs) {
    Write-Output "Status: SUCCESS. GUI processes are still running after 10s."
    foreach ($p in $finalProcs) {
        Write-Output "Terminating PID: $($p.ProcessId)"
        Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
    }
} else {
    Write-Output "Status: FAILURE. No related processes found after 10s."
}
