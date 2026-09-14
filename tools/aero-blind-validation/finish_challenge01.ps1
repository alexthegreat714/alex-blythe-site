param(
  [string]$Package = "public/demos/aero/blind-validation-01-run-v1",
  [string]$Output = "output/challenge01/production-v1",
  [string]$KeyFile = "D:/AeroChallengeCustody/ch01/challenge01.key"
)
$ErrorActionPreference = 'Stop'
$repo = (Get-Location).Path
function Run-Python([string[]]$CommandArgs) {
  & python @CommandArgs | Out-Host
  if ($LASTEXITCODE -ne 0) { throw "Python command failed ($LASTEXITCODE): $($CommandArgs -join ' ')" }
}
function Invoke-Git([string[]]$CommandArgs) {
  & git @CommandArgs | Out-Host
  if ($LASTEXITCODE -ne 0) { throw "Git command failed ($LASTEXITCODE): $($CommandArgs -join ' ')" }
}
function Commit-IfChanges([string]$Message) {
  & git diff --cached --quiet
  if ($LASTEXITCODE -eq 1) { Invoke-Git -CommandArgs @('commit','-m',$Message) }
  elseif ($LASTEXITCODE -ne 0) { throw "Git staged status failed ($LASTEXITCODE)" }
  return (& git rev-parse HEAD).Trim()
}

Write-Output "Waiting for the retained 54-case sweep..."
while ($true) {
  $progress = Get-Content (Join-Path $Output 'progress.json') -Raw | ConvertFrom-Json
  Write-Output ("{0}: {1}/{2}; active: {3}" -f $progress.updated_at,$progress.completed,$progress.total,($progress.running -join ', '))
  if ([int]$progress.completed -eq [int]$progress.total -and @($progress.running).Count -eq 0) { break }
  Start-Sleep -Seconds 30
}

$pkg = Join-Path $repo $Package
$out = Join-Path $repo $Output
Write-Output "All attempts finished. Freezing retained predictions without opening the reference."
Run-Python -CommandArgs @('tools/aero-blind-validation/freeze_sweep.py',$Package,$Output)
Invoke-Git -CommandArgs @('add',"$Package/evidence", "$Package/blind_prediction.json", "$Package/blind_prediction.md", "$Package/state.json")
$predictionCommit = Commit-IfChanges 'Freeze Challenge 01 prediction and retained case evidence'
Invoke-Git -CommandArgs @('push','origin','main')
Run-Python -CommandArgs @('tools/aero-blind-validation/protocol.py',$Package,'anchor','--commit',$predictionCommit)
Invoke-Git -CommandArgs @('add',"$Package/state.json")
$predictionAnchorCommit = Commit-IfChanges 'Anchor Challenge 01 prediction checkpoint'
Write-Output "Prediction anchored at $predictionAnchorCommit. Unsealing the external reference now."

Run-Python -CommandArgs @('tools/aero-blind-validation/protocol.py',$Package,'unseal','--key-file',$KeyFile)
Run-Python -CommandArgs @('tools/aero-blind-validation/protocol.py',$Package,'compare')
Invoke-Git -CommandArgs @('add',"$Package/reference.csv", "$Package/comparison.json", "$Package/state.json")
$comparisonCommit = Commit-IfChanges 'Reveal and compare Challenge 01 reference'
Invoke-Git -CommandArgs @('push','origin','main')
Run-Python -CommandArgs @('tools/aero-blind-validation/protocol.py',$Package,'anchor','--commit',$comparisonCommit)
Invoke-Git -CommandArgs @('add',"$Package/state.json")
$comparisonAnchorCommit = Commit-IfChanges 'Anchor Challenge 01 comparison checkpoint'

Write-Output "Comparison anchored at $comparisonAnchorCommit. Generating paper and figures from actual results."
Run-Python -CommandArgs @('tools/aero-blind-validation/experiment_report.py',$Package)
$compile = 'C:/Users/blyth/.codex/plugins/cache/openai-bundled/latex/0.2.6/scripts/compile_latex.py'
Run-Python -CommandArgs @($compile,"$Package/report/paper.tex",'--output-directory',"$Package/report",'--json')

$preview = Join-Path $repo 'output/challenge01/report-preview'
if (Test-Path -LiteralPath $preview) { Remove-Item -LiteralPath $preview -Recurse -Force }
New-Item -ItemType Directory -Path $preview | Out-Null
$pdfinfo = Get-Command pdfinfo -ErrorAction SilentlyContinue
if ($pdfinfo) {
  $pages = (& pdfinfo "$Package/report/paper.pdf" | Select-String '^Pages:' | ForEach-Object { [int](($_ -split ':')[1].Trim()) })
  Write-Output "Paper pages: $pages"
  if ($pages -lt 6 -or $pages -gt 12) { throw "Paper page count outside the declared 6-10 target: $pages" }
}
$pdftoppm = Get-Command pdftoppm -ErrorAction SilentlyContinue
if ($pdftoppm) { & pdftoppm -png -r 120 "$Package/report/paper.pdf" "$preview/paper" }

Run-Python -CommandArgs @('tools/aero-blind-validation/package_release.py',$Package)
Run-Python -CommandArgs @('scripts/challenge01_status.py')
Invoke-Git -CommandArgs @('add',"$Package/manifest.json", "$Package/reproduction.zip", "$Package/report", "$Package/code", "$Package/current-status.json", "$Package/state.json",'tools/aero-blind-validation/finish_challenge01.ps1')
$releaseCommit = Commit-IfChanges 'Publish complete Challenge 01 report and reproduction release'
Invoke-Git -CommandArgs @('push','origin','main')
Write-Output "Release pushed at $releaseCommit. Build and local final QA follow."

$staging = Join-Path $repo 'output/challenge01/final-release'
if (Test-Path -LiteralPath $staging) { Remove-Item -LiteralPath $staging -Recurse -Force }
New-Item -ItemType Directory -Path $staging | Out-Null
Invoke-Git -CommandArgs @('-c','core.autocrlf=false','checkout-index','--all','--force',"--prefix=$staging/")
$junction = Join-Path $staging 'node_modules'
New-Item -ItemType Junction -Path $junction -Target (Join-Path $repo 'node_modules') | Out-Null
Push-Location $staging
try { & npm run build; if ($LASTEXITCODE -ne 0) { throw "Astro build failed ($LASTEXITCODE)" } }
finally { Pop-Location }

$server = Start-Process -FilePath python -ArgumentList @('-m','http.server','4327','--bind','127.0.0.1','--directory',(Join-Path $staging 'dist')) -PassThru -WindowStyle Hidden
try {
  Start-Sleep -Seconds 2
  & node scripts/aero-challenge-release.test.cjs 'http://127.0.0.1:4327' 'output/challenge01/final-release-qa'
  if ($LASTEXITCODE -ne 0) { throw "Final release QA failed ($LASTEXITCODE)" }
} finally { Stop-Process -Id $server.Id -Force -ErrorAction SilentlyContinue }

Write-Output "Local release QA passed. Waiting for GitHub Pages deployment."
for ($i=0; $i -lt 30; $i++) {
  $run = Invoke-RestMethod 'https://api.github.com/repos/alexthegreat714/alex-blythe-site/actions/runs?per_page=1'
  $latest = $run.workflow_runs[0]
  Write-Output ("CI {0}: {1} {2}" -f $latest.head_sha,$latest.status,$latest.conclusion)
  if ($latest.head_sha -eq $releaseCommit -and $latest.status -eq 'completed') {
    if ($latest.conclusion -ne 'success') { throw 'Deployment workflow failed' }
    break
  }
  Start-Sleep -Seconds 20
}
& node scripts/aero-challenge-release.test.cjs 'https://alex-blythe.com' 'output/challenge01/final-release-live-qa'
if ($LASTEXITCODE -ne 0) { throw "Live final release QA failed ($LASTEXITCODE)" }
Write-Output "Challenge 01 release and deployed QA complete."
