$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $PSScriptRoot
$source = Join-Path $projectRoot 'exports\PROJECT FALCON -V2.fbx'
$destinationBase = Join-Path $projectRoot 'dashboard-next\public\models\PROJECT-FALCON-V2'
$toolDirectory = Join-Path $env:TEMP 'falcon-fbx2gltf-tool'
$converter = Join-Path $toolDirectory 'node_modules\fbx2gltf\bin\Windows_NT\FBX2glTF.exe'

if (-not (Test-Path -LiteralPath $source)) {
    throw "FBX source not found: $source"
}
if (-not (Test-Path -LiteralPath $converter)) {
    New-Item -ItemType Directory -Force -Path $toolDirectory | Out-Null
    & npm.cmd install --prefix $toolDirectory fbx2gltf@0.9.7-p1 --no-save
    if ($LASTEXITCODE -ne 0) { throw 'Could not install the pinned FBX converter.' }
}

& $converter --binary --input $source --output $destinationBase
if ($LASTEXITCODE -ne 0) { throw 'FBX-to-GLB conversion failed.' }

Write-Host "Dashboard model updated: $destinationBase.glb"
