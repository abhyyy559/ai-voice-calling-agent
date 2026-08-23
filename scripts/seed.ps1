<#
.SYNOPSIS
    Seed the demo tenant INSIDE the running backend container.
    Creates (idempotently): org "Demo University", owner demo@example.com /
    demo1234, agent "Absent Student Follow-up" v1 (from
    domain-configs/absent-student.json), a draft campaign + 5 sample contacts.

.DESCRIPTION
    Requires the stack from scripts\dev-up.ps1 to be running. The seed script
    never places calls and contains no secrets.

.USAGE
    powershell -ExecutionPolicy Bypass -File scripts\seed.ps1
#>

$ErrorActionPreference = 'Stop'

$Root        = Split-Path -Parent $PSScriptRoot          # repo root
$ComposeFile = Join-Path $Root 'infra\docker-compose.yml'
$EnvFile     = Join-Path $Root '.env'

Write-Host '=== AI Voice Calling Agent - seed ===' -ForegroundColor Cyan

& docker compose -f $ComposeFile --env-file $EnvFile exec backend python scripts/seed_demo.py
if ($LASTEXITCODE -ne 0) {
    Write-Host '[seed] ERROR: seeding failed.' -ForegroundColor Red
    Write-Host '[seed] Is the stack running? Start it first:' -ForegroundColor Red
    Write-Host '[seed]   powershell -ExecutionPolicy Bypass -File scripts\dev-up.ps1' -ForegroundColor Red
    Write-Host '[seed] Then inspect: docker compose -f infra\docker-compose.yml --env-file .env logs backend' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host '[seed] Done. Log in at http://localhost:3000 with:' -ForegroundColor Green
Write-Host '[seed]   email:    demo@example.com'
Write-Host '[seed]   password: demo1234'
