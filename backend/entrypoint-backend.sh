#!/bin/bash
set -e

echo "执行数据库迁移..."
python manage.py migrate --noinput

# 创建管理员用户（如果环境变量存在）
if [ -n "$DJANGO_ADMIN_USERNAME" ] && [ -n "$DJANGO_ADMIN_PASSWORD" ]; then
    echo "创建管理员用户..."
    python manage.py createsuperuser --noinput --username "$DJANGO_ADMIN_USERNAME" --email admin@example.com || true
fi

exec "$@"
