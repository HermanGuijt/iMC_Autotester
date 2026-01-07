# BeagleBone SSH Helper Script
# Gebruik: .\bb.ps1 "commando"

$BB_HOST = "debian@192.168.178.179"
$BB_PASS = "temppwd"

if ($args.Count -eq 0) {
    # Interactieve SSH sessie
    Write-Host "Verbinden met BeagleBone..." -ForegroundColor Green
    $env:SSHPASS = $BB_PASS
    ssh $BB_HOST
} else {
    # Voer commando uit
    $command = $args -join " "
    Write-Host "Uitvoeren: $command" -ForegroundColor Cyan
    echo $BB_PASS | ssh $BB_HOST $command
}
