[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$RepositoryRoot,
    [Parameter(Mandatory)]
    [ValidateSet('Restore', 'Build', 'Test', 'TestBrowser', 'StartBackend', 'StartFrontend')]
    [string]$Action
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Resolve-RequiredPath {
    param(
        [Parameter(Mandatory)]
        [string]$Path,
        [Parameter(Mandatory)]
        [string]$Description,
        [switch]$Directory
    )

    if (-not (Test-Path -LiteralPath $Path)) {
        throw "$Description was not found: $Path"
    }

    $item = Get-Item -LiteralPath $Path
    if ($Directory -and -not $item.PSIsContainer) {
        throw "$Description is not a directory: $Path"
    }
    if (-not $Directory -and $item.PSIsContainer) {
        throw "$Description is not a file: $Path"
    }

    return $item.FullName
}

function Resolve-NativeExecutable {
    param(
        [Parameter(Mandatory)]
        [string]$Name
    )

    $command = Get-Command -Name $Name -CommandType Application -ErrorAction Stop |
        Select-Object -First 1
    return [string]$command.Path
}

function Invoke-Native {
    param(
        [Parameter(Mandatory)]
        [string]$Executable,
        [Parameter(Mandatory)]
        [string[]]$Arguments,
        [Parameter(Mandatory)]
        [string]$WorkingDirectory,
        [Parameter(Mandatory)]
        [ref]$ExitCode
    )

    Push-Location -LiteralPath $WorkingDirectory
    try {
        & $Executable @Arguments
        $ExitCode.Value = [int]$LASTEXITCODE
    }
    finally {
        Pop-Location
    }
}

function Invoke-CheckedNative {
    param(
        [Parameter(Mandatory)]
        [string]$Executable,
        [Parameter(Mandatory)]
        [string[]]$Arguments,
        [Parameter(Mandatory)]
        [string]$WorkingDirectory
    )

    $exitCode = 0
    Invoke-Native `
        -Executable $Executable `
        -Arguments $Arguments `
        -WorkingDirectory $WorkingDirectory `
        -ExitCode ([ref]$exitCode)

    if ($exitCode -ne 0) {
        [Console]::Error.WriteLine(
            "Native command failed with exit code ${exitCode}: $Executable $($Arguments -join ' ')"
        )
        exit $exitCode
    }
}

$repositoryPath = Resolve-RequiredPath `
    -Path $RepositoryRoot `
    -Description 'Repository root' `
    -Directory
$pocPath = Resolve-RequiredPath `
    -Path (Join-Path $repositoryPath 'poc') `
    -Description 'POC directory' `
    -Directory
$dotnetExecutable = Resolve-NativeExecutable -Name 'dotnet.exe'
$npmExecutable = Resolve-NativeExecutable -Name 'npm.cmd'

switch ($Action) {
    'Restore' {
        $backendPath = Resolve-RequiredPath `
            -Path (Join-Path $pocPath 'backend') `
            -Description 'Backend project directory' `
            -Directory
        $backendTestsPath = Resolve-RequiredPath `
            -Path (Join-Path $pocPath 'backend.tests') `
            -Description 'Backend test project directory' `
            -Directory
        $frontendPath = Resolve-RequiredPath `
            -Path (Join-Path $pocPath 'frontend') `
            -Description 'Frontend project directory' `
            -Directory
        $backendProject = Resolve-RequiredPath `
            -Path (Join-Path $backendPath 'Poc.Api.csproj') `
            -Description 'Backend project'
        $backendTestsProject = Resolve-RequiredPath `
            -Path (Join-Path $backendTestsPath 'Poc.Api.Tests.csproj') `
            -Description 'Backend test project'
        $frontendPackage = Resolve-RequiredPath `
            -Path (Join-Path $frontendPath 'package.json') `
            -Description 'Frontend package manifest'
        Invoke-CheckedNative `
            -Executable $dotnetExecutable `
            -Arguments @('restore', $backendProject, '--locked-mode', '--verbosity', 'minimal') `
            -WorkingDirectory $backendPath
        Invoke-CheckedNative `
            -Executable $dotnetExecutable `
            -Arguments @('restore', $backendTestsProject, '--locked-mode', '--verbosity', 'minimal') `
            -WorkingDirectory $backendTestsPath
        Invoke-CheckedNative `
            -Executable $npmExecutable `
            -Arguments @('ci') `
            -WorkingDirectory $frontendPath

        $playwrightExecutable = Resolve-RequiredPath `
            -Path (Join-Path $frontendPath 'node_modules\.bin\playwright.cmd') `
            -Description 'Playwright executable'
        Invoke-CheckedNative `
            -Executable $playwrightExecutable `
            -Arguments @('install', 'chromium') `
            -WorkingDirectory $frontendPath
    }
    'Build' {
        $backendPath = Resolve-RequiredPath `
            -Path (Join-Path $pocPath 'backend') `
            -Description 'Backend project directory' `
            -Directory
        $frontendPath = Resolve-RequiredPath `
            -Path (Join-Path $pocPath 'frontend') `
            -Description 'Frontend project directory' `
            -Directory
        $backendProject = Resolve-RequiredPath `
            -Path (Join-Path $backendPath 'Poc.Api.csproj') `
            -Description 'Backend project'
        $frontendPackage = Resolve-RequiredPath `
            -Path (Join-Path $frontendPath 'package.json') `
            -Description 'Frontend package manifest'
        Invoke-CheckedNative `
            -Executable $dotnetExecutable `
            -Arguments @('build', $backendProject, '--no-restore', '--verbosity', 'minimal') `
            -WorkingDirectory $backendPath
        Invoke-CheckedNative `
            -Executable $npmExecutable `
            -Arguments @('run', 'build', '--', '--configuration', 'production') `
            -WorkingDirectory $frontendPath
    }
    'Test' {
        $backendTestsPath = Resolve-RequiredPath `
            -Path (Join-Path $pocPath 'backend.tests') `
            -Description 'Backend test project directory' `
            -Directory
        $frontendPath = Resolve-RequiredPath `
            -Path (Join-Path $pocPath 'frontend') `
            -Description 'Frontend project directory' `
            -Directory
        $backendTestsProject = Resolve-RequiredPath `
            -Path (Join-Path $backendTestsPath 'Poc.Api.Tests.csproj') `
            -Description 'Backend test project'
        $frontendPackage = Resolve-RequiredPath `
            -Path (Join-Path $frontendPath 'package.json') `
            -Description 'Frontend package manifest'
        Invoke-CheckedNative `
            -Executable $dotnetExecutable `
            -Arguments @('test', $backendTestsProject, '--no-restore', '--verbosity', 'minimal') `
            -WorkingDirectory $backendTestsPath
        Invoke-CheckedNative `
            -Executable $npmExecutable `
            -Arguments @('run', 'test', '--', '--watch=false') `
            -WorkingDirectory $frontendPath
    }
    'TestBrowser' {
        $frontendPath = Resolve-RequiredPath `
            -Path (Join-Path $pocPath 'frontend') `
            -Description 'Frontend project directory' `
            -Directory
        $testsPath = Resolve-RequiredPath `
            -Path (Join-Path $pocPath 'tests') `
            -Description 'Browser test directory' `
            -Directory
        $frontendPackage = Resolve-RequiredPath `
            -Path (Join-Path $frontendPath 'package.json') `
            -Description 'Frontend package manifest'
        $playwrightConfig = Resolve-RequiredPath `
            -Path (Join-Path $testsPath 'playwright.config.ts') `
            -Description 'Playwright configuration'
        $playwrightExecutable = Resolve-RequiredPath `
            -Path (Join-Path $frontendPath 'node_modules\.bin\playwright.cmd') `
            -Description 'Playwright executable'
        Invoke-CheckedNative `
            -Executable $playwrightExecutable `
            -Arguments @(
                'test',
                '--config',
                $playwrightConfig,
                '--project',
                'chromium',
                '--workers',
                '1'
            ) `
            -WorkingDirectory $testsPath
    }
    'StartBackend' {
        $backendPath = Resolve-RequiredPath `
            -Path (Join-Path $pocPath 'backend') `
            -Description 'Backend project directory' `
            -Directory
        $backendProject = Resolve-RequiredPath `
            -Path (Join-Path $backendPath 'Poc.Api.csproj') `
            -Description 'Backend project'
        Invoke-CheckedNative `
            -Executable $dotnetExecutable `
            -Arguments @(
                'run',
                '--project',
                $backendProject,
                '--launch-profile',
                'Poc.Api',
                '--no-restore'
            ) `
            -WorkingDirectory $backendPath
    }
    'StartFrontend' {
        $frontendPath = Resolve-RequiredPath `
            -Path (Join-Path $pocPath 'frontend') `
            -Description 'Frontend project directory' `
            -Directory
        $frontendPackage = Resolve-RequiredPath `
            -Path (Join-Path $frontendPath 'package.json') `
            -Description 'Frontend package manifest'
        Invoke-CheckedNative `
            -Executable $npmExecutable `
            -Arguments @('start', '--', '--host', 'localhost', '--port', '4200') `
            -WorkingDirectory $frontendPath
    }
}
