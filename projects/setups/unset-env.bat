REM Run using source unset-env.sh

echo "Unsetting environment variables."

setx SQLITE_URL ""

setx ACCESS_TOKEN_KEY ""
setx TOKEN_EXPIRE_MINUTES 0
setx ALGORITHM ""
setx LAND_LEND_IMAGES_DIR ""

echo "Done!"