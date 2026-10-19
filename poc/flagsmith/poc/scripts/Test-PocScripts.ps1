[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$RepositoryRoot
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repositoryPath = [System.IO.Path]::GetFullPath($RepositoryRoot)
$helperPath = Join-Path ([System.IO.Path]::GetFullPath($PSScriptRoot)) 'Invoke-Poc.ps1'
$parser = [System.Management.Automation.Language.Parser]
$tokens = $null
$parseErrors = $null

if (-not (Test-Path -LiteralPath $helperPath -PathType Leaf)) {
    throw "Helper script was not found: $helperPath"
}

$null = $parser::ParseFile($helperPath, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count -ne 0) {
    $details = $parseErrors | ForEach-Object { $_.Message } | Join-String -Separator '; '
    throw "Helper parser errors: $details"
}

function Invoke-PocHelper {
    param(
        [Parameter(Mandatory)]
        [string]$Root,
        [Parameter(Mandatory)]
        [string]$Action,
        [string]$WorkingDirectory
    )

    $pwsh = (Get-Command -Name 'pwsh.exe' -CommandType Application -ErrorAction Stop).Source
    $arguments = [System.Collections.Generic.List[string]]::new()
    $arguments.Add('-NoLogo')
    $arguments.Add('-NoProfile')
    $arguments.Add('-NonInteractive')
    if ($PSBoundParameters.ContainsKey('WorkingDirectory')) {
        $arguments.Add('-WorkingDirectory')
        $arguments.Add($WorkingDirectory)
    }
    $arguments.Add('-File')
    $arguments.Add($helperPath)
    $arguments.Add('-RepositoryRoot')
    $arguments.Add($Root)
    $arguments.Add('-Action')
    $arguments.Add($Action)

    & $pwsh @arguments | ForEach-Object { Write-Host $_ }
    $childExitCode = $LASTEXITCODE
    return $childExitCode
}

function Assert-NonZeroExitCode {
    param(
        [Parameter(Mandatory)]
        [int]$ExitCode,
        [Parameter(Mandatory)]
        [string]$Description
    )

    if ($ExitCode -eq 0) {
        throw "$Description unexpectedly succeeded."
    }
}

$fixtureRoot = Join-Path (
    Join-Path $HOME '.copilot\session-state'
) ("task-5-helper-fixture with spaces-" + [Guid]::NewGuid().ToString('N'))
$frontendPath = Join-Path $fixtureRoot 'poc\frontend'
$recordPath = Join-Path $fixtureRoot 'frontend-record.json'
$originalRecordSetting = $env:POC_FIXTURE_RECORD
$originalExitSetting = $env:POC_EXPECTED_EXIT_CODE

try {
    $unknownActionExitCode = Invoke-PocHelper -Root $repositoryPath -Action 'NotAnAction'
    Assert-NonZeroExitCode -ExitCode $unknownActionExitCode -Description 'Unknown action validation'

    $missingRoot = Join-Path $fixtureRoot 'does not exist'
    $missingRootExitCode = Invoke-PocHelper -Root $missingRoot -Action 'Build'
    Assert-NonZeroExitCode -ExitCode $missingRootExitCode -Description 'Nonexistent repository root validation'

    New-Item -ItemType Directory -Path $frontendPath -Force | Out-Null
    @'
{
  "name": "poc-helper-fixture",
  "private": true,
  "scripts": {
    "start": "node record.cjs"
  }
}
'@ | Set-Content -LiteralPath (Join-Path $frontendPath 'package.json') -Encoding utf8
    @'
const fs = require('fs');

const output = process.env.POC_FIXTURE_RECORD;
fs.writeFileSync(output, JSON.stringify({
  cwd: process.cwd(),
  args: process.argv.slice(2)
}));

if (process.env.POC_EXPECTED_EXIT_CODE) {
  process.exit(Number(process.env.POC_EXPECTED_EXIT_CODE));
}
'@ | Set-Content -LiteralPath (Join-Path $frontendPath 'record.cjs') -Encoding utf8

    $env:POC_FIXTURE_RECORD = $recordPath
    Remove-Item Env:POC_EXPECTED_EXIT_CODE -ErrorAction SilentlyContinue
    $fixtureStartExitCode = Invoke-PocHelper `
        -Root $fixtureRoot `
        -Action 'StartFrontend' `
        -WorkingDirectory ([Environment]::SystemDirectory)
    if ($fixtureStartExitCode -ne 0) {
        throw "Fixture StartFrontend failed with exit code $fixtureStartExitCode."
    }

    if (-not (Test-Path -LiteralPath $recordPath -PathType Leaf)) {
        throw 'Fixture did not record the forwarded command.'
    }

    $record = Get-Content -LiteralPath $recordPath -Raw | ConvertFrom-Json
    if ($record.cwd -ne $frontendPath) {
        throw "Expected frontend working directory '$frontendPath', got '$($record.cwd)'."
    }

    $expectedArguments = @('--host', 'localhost', '--port', '4200')
    $actualArguments = @($record.args | ForEach-Object { [string]$_ })
    $expectedArgumentsJson = $expectedArguments | ConvertTo-Json -Compress
    $actualArgumentsJson = $actualArguments | ConvertTo-Json -Compress
    if ($actualArgumentsJson -cne $expectedArgumentsJson) {
        throw "Expected npm arguments '$($expectedArguments -join ' ')', got '$($actualArguments -join ' ')'."
    }

    $env:POC_EXPECTED_EXIT_CODE = '37'
    $nativeFailureExitCode = Invoke-PocHelper `
        -Root $fixtureRoot `
        -Action 'StartFrontend' `
        -WorkingDirectory ([Environment]::SystemDirectory)
    if ($nativeFailureExitCode -ne 37) {
        throw "Expected native exit code 37 to propagate, got $nativeFailureExitCode."
    }
}
finally {
    if ($null -eq $originalRecordSetting) {
        Remove-Item Env:POC_FIXTURE_RECORD -ErrorAction SilentlyContinue
    }
    else {
        $env:POC_FIXTURE_RECORD = $originalRecordSetting
    }

    if ($null -eq $originalExitSetting) {
        Remove-Item Env:POC_EXPECTED_EXIT_CODE -ErrorAction SilentlyContinue
    }
    else {
        $env:POC_EXPECTED_EXIT_CODE = $originalExitSetting
    }

    if (Test-Path -LiteralPath $fixtureRoot) {
        Remove-Item -LiteralPath $fixtureRoot -Recurse -Force
    }
}

Write-Output 'Test-PocScripts: PASS'
