@echo off

echo "Exporting environment variables for use by the WebAPI."

setx SQLITE_URL "sqlite:///land_lend.db"
echo "Set SQLITE_URL env"

setx POSTGRESQL_URL "postgresql://postgres:postgres@127.0.0.1:5432/land_lend_db"
echo "Set POSTGRESQL_URL env"

REM WARNING regenerate access token key.
setx ACCESS_TOKEN_KEY "e9623a04fd79f49dd476f00ef4d4200209c147b83dc5db410d0d66500ef77beb"
echo "Set ACCESS_TOKEN_KEY env"

setx TOKEN_EXPIRE_MINUTES 45
echo "Set TOKEN_EXPIRE_MINUTES env"

setx ALGORITHM "HS256"
echo "Set ALGORITHM env"

echo "Done!"