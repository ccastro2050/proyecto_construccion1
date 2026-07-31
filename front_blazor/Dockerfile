# ==============================================================
# Front Blazor — Blazor Server / .NET 10 (puerto 8004)
#
# Usa la imagen SDK (no la runtime) porque el contenedor corre
# "dotnet watch": al guardar un .razor o .cs recompila y reinicia
# solo, igual que --reload en las APIs Python y --debug en Flask.
# ==============================================================
FROM mcr.microsoft.com/dotnet/sdk:10.0

WORKDIR /app

# Primero solo el .csproj: si no cambian las dependencias,
# Docker reutiliza la capa del restore (arranques más rápidos).
COPY FrontBlazorTutorial.csproj ./
RUN dotnet restore FrontBlazorTutorial.csproj

# Después el resto del código (en desarrollo queda tapado por el
# volumen que monta docker-compose.yml, y eso es lo esperado).
COPY . .

# El watcher de archivos por eventos no ve los cambios que llegan
# por volúmenes montados desde Windows: se usa sondeo (polling).
ENV DOTNET_USE_POLLING_FILE_WATCHER=true \
    ASPNETCORE_ENVIRONMENT=Development \
    ASPNETCORE_URLS=http://0.0.0.0:8004

EXPOSE 8004

# --no-launch-profile ignora launchSettings.json (puertos locales)
# y respeta ASPNETCORE_URLS definido arriba.
CMD ["dotnet", "watch", "--project", "FrontBlazorTutorial.csproj", "run", "--no-launch-profile"]
