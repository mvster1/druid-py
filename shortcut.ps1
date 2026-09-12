# creates druid.lnk. usage: powershell -ExecutionPolicy Bypass -File shortcut.ps1 [folder]
# no folder given: creates it next to this script. the shortcut works from anywhere.

$root = $PSScriptRoot
if ($args[0]) { $dest = (Resolve-Path $args[0]).Path } else { $dest = $root }

$py = & python -c "import os,sys;w=os.path.join(os.path.dirname(sys.executable),'pythonw.exe');print(w if os.path.exists(w) else sys.executable)"
if (-not $py) { throw "python not found in PATH" }

$lnk = (New-Object -ComObject WScript.Shell).CreateShortcut((Join-Path $dest "druid.lnk"))
$lnk.TargetPath = $py
$lnk.Arguments = '"' + (Join-Path $root "druid.py") + '"'
$lnk.WorkingDirectory = $root
$lnk.IconLocation = Join-Path $root "icon.ico"
$lnk.Description = "batch image resizer"
$lnk.Save()

Write-Output ("created " + (Join-Path $dest "druid.lnk") + " -> " + $py)
