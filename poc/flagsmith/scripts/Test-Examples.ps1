[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$RepositoryRoot,
    [switch]$Restore,
    [ValidateNotNullOrEmpty()]
    [string]$NuGetSource = 'https://api.nuget.org/v3/index.json'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$root = (Resolve-Path -LiteralPath $RepositoryRoot).Path
$skill = Join-Path $root '.github\skills\openfeature-flagsmith-dotnet'
$angular = Join-Path $skill 'examples\angular'
$dotnet = Join-Path $skill 'examples\dotnet\LocalEvaluation.csproj'
$node = (Get-Command -Name node -CommandType Application).Source
$dotnetExecutable = (Get-Command -Name dotnet -CommandType Application).Source
$npm = (Get-Command -Name npm).Source
foreach ($required in @($dotnet, (Join-Path $angular 'package.json'), (Join-Path $root 'scripts\validate-skill.mjs'))) {
    if (-not (Test-Path -LiteralPath $required -PathType Leaf)) {
        throw "Required reference file is missing: $required"
    }
}

Push-Location -LiteralPath $root
try {
    $tokens = $null
    $parseErrors = $null
    $null = [System.Management.Automation.Language.Parser]::ParseFile(
        $PSCommandPath, [ref]$tokens, [ref]$parseErrors)
    if ($parseErrors.Count -gt 0) {
        throw ($parseErrors | Out-String)
    }

    [string[]]$arguments = @((Join-Path $root 'scripts\validate-skill.mjs'))
    & $node @arguments
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    if ($Restore) {
        [string[]]$arguments = @('restore', $dotnet, '--source', $NuGetSource, '--locked-mode', '--verbosity', 'quiet')
        & $dotnetExecutable @arguments
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        Push-Location -LiteralPath $angular
        try {
            [string[]]$arguments = @('ci', '--ignore-scripts', '--no-audit', '--no-fund')
            & $npm @arguments
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        } finally {
            Pop-Location
        }
    }

    [string[]]$arguments = @('run', '--project', $dotnet, '--no-restore', '--verbosity', 'quiet')
    & $dotnetExecutable @arguments
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

    Push-Location -LiteralPath $angular
    try {
        [string[]]$arguments = @('test')
        & $npm @arguments
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } finally {
        Pop-Location
    }
} finally {
    Pop-Location
}
