Write-Host "Copiando logo do Windows para WSL..." -ForegroundColor Green

$source = "C:\Users\resper\Downloads\gabi.svg"
$destination = "\\wsl$\Ubuntu\home\resper\gabi-ai\nova-aplicacao\frontend\public\logo.svg"

if (Test-Path $source) {
    try {
        Copy-Item -Path $source -Destination $destination -Force
        Write-Host "Logo copiado com sucesso!" -ForegroundColor Green
        Write-Host "Arquivo salvo em: $destination" -ForegroundColor Yellow
    }
    catch {
        Write-Host "Erro ao copiar o arquivo: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "Arquivo não encontrado em: $source" -ForegroundColor Red
}

Read-Host "Pressione Enter para continuar..." 