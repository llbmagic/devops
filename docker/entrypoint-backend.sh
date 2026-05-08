#!/bin/bash
set -e

echo "等待 MySQL TCP 端口就绪..."

host="${DATABASE_HOST:-mysql}"
port="${DATABASE_PORT:-3306}"
max_wait=60
counter=0

until nc -z "$host" "$port" 2>/dev/null; do
    counter=$((counter + 1))
    if [ $counter -eq $max_wait ]; then
        echo "MySQL TCP 连接超时"
        exit 1
    fi
    echo "等待 MySQL TCP 端口... ($counter/$max_wait)"
    sleep 2
done

echo "MySQL TCP 端口已就绪"

echo "执行数据库迁移..."
python manage.py migrate --noinput

# 创建管理员用户（如果环境变量存在）
if [ -n "$DJANGO_ADMIN_USERNAME" ] && [ -n "$DJANGO_ADMIN_PASSWORD" ]; then
    echo "创建管理员用户..."
    python manage.py createsuperuser --noinput --username "$DJANGO_ADMIN_USERNAME" --email admin@example.com || true
fi

exec "$@"
