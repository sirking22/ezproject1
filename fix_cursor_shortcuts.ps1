# PowerShell script to fix Cursor shortcuts and clean updater logs
$oldPath = "Z:\Файлы\VS code\cursor\Cursor.exe"
$newPath = "Z:\Files\VS_code\cursor\Cursor.exe"
$searchDirs = @(
    "$env:USERPROFILE\Desktop",
    "$env:APPDATA\Microsoft\Windows\Start Menu\Programs"
)

Write-Host "--- Searching and fixing Cursor shortcuts ---"
foreach ($dir in $searchDirs) {
    Get-ChildItem -Path $dir -Filter "*.lnk" -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut($_.FullName)
        if ($shortcut.TargetPath -eq $oldPath) {
            Write-Host "Fixing shortcut: $_.FullName"
            $shortcut.TargetPath = $newPath
            $shortcut.Save()
        }
    }
}

Write-Host "--- Checking if Cursor.exe exists at new path ---"
if (Test-Path $newPath) {
    Write-Host "Cursor.exe found at new path: $newPath"
}
else {
    Write-Host "WARNING: Cursor.exe NOT found at new path!"
}

Write-Host "--- Cleaning Cursor updater temp logs ---"
Get-ChildItem "$env:TEMP" -Filter "cursor-inno-updater-*.log" | Remove-Item -Force -ErrorAction SilentlyContinue
Write-Host "Done. All actions completed." 