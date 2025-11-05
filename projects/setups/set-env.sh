# Run using source set-env.sh

echo 'Exporting environment variables for use by the WebAPI.'

if [ -n SQLITE_URL ]; then
    SQLITE_URL="sqlite:///land_lend.db"
    export SQLITE_URL
    echo 'Set SQLITE_URL env'
fi

if [ -n POSTGRESQL_URL ]; then
    POSTGRESQL_URL="postgresql://postgres:postgres@127.0.0.1:5432/land_lend_db"
    export POSTGRESQL_URL
    echo 'Set POSTGRESQL_URL env'
fi

if [ -n ACCESS_TOKEN_KEY ]; then
    # WARNING regenerate access token key.
    # To regenerate new ACCESS_TOKEN_KEY, run: openssl rand -hex 32 # 32 is the rand length.
    ACCESS_TOKEN_KEY="e9623a04fd79f49dd476f00ef4d4200209c147b83dc5db410d0d66500ef77beb"
    export ACCESS_TOKEN_KEY
    echo 'Set ACCESS_TOKEN_KEY env'
fi

if [ -n TOKEN_EXPIRE_MINUTES ]; then
    TOKEN_EXPIRE_MINUTES=45
    export TOKEN_EXPIRE_MINUTES
    echo 'Set TOKEN_EXPIRE_MINUTES env'
fi

if [ -n ALGORITHM ]; then
    ALGORITHM="HS256"
    export ALGORITHM
    echo 'Set ALGORITHM env'
fi

if [ -n LAND_LEND_IMAGES_DIR ]; then
    LAND_LEND_IMAGES_DIR="/var/land_lend/images"
    export LAND_LEND_IMAGES_DIR
    echo 'Set LAND_LEND_FILES_DIR env'
fi

echo 'Done!'

#echo 'If environment variables not found re-run using: source set-env.sh'