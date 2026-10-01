# Kills only the live_watch.py process (matched by command line), nothing else named python.exe.
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -like '*live_watch.py*' } |
    ForEach-Object {
        Write-Output "stopping pid $($_.ProcessId)"
        Stop-Process -Id $_.ProcessId -Force
    }
