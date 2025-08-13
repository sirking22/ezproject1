# Import-DotEnv.ps1 — lightweight .env loader for the current PowerShell process
# Usage: . tools/Import-DotEnv.ps1; Import-DotEnv -Path .\.env -Quiet

param()

function Import-DotEnv {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [string]$Path = (Join-Path -Path (Get-Location) -ChildPath '.env'),
        [Parameter(Mandatory = $false)]
        [switch]$Quiet
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        if (-not $Quiet) { Write-Verbose (".env not found at: {0}" -f $Path) }
        return
    }

    # Read UTF-8 without BOM to avoid odd chars
    $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
    $lines = [System.IO.File]::ReadAllLines($Path, $utf8NoBom)

    foreach ($raw in $lines) {
        if ($raw -match '^[\s]*($|#)') { continue }
        $line = $raw.Trim()
        if ($line.StartsWith('export ')) { $line = $line.Substring(7) }
        $kv = $line -split '=', 2
        if ($kv.Count -lt 2) { continue }
        $key = $kv[0].Trim()
        $val = $kv[1].Trim()
        # Strip surrounding quotes
        $val = $val.Trim('"').Trim("'")
        if (-not $key) { continue }
        # Set for current process only (no leaks to registry). Do not echo secrets.
        [Environment]::SetEnvironmentVariable($key, $val, 'Process')
    }

    if (-not $Quiet) {
        Write-Host ("DotEnv imported: {0}" -f (Resolve-Path -LiteralPath $Path))
    }
}
