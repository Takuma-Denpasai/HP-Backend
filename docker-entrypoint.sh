#!/bin/sh

set -e

# データベースのマイグレーションを実行
echo "Applying database migrations..."
python manage.py migrate

# 管理者ユーザーを作成
echo "Creating admin user..."
python manage.py create_admin --username admin --password admin_user --email "admin@example.com"

# サーバーを起動
echo "Starting server..."
exec "$@"