#!/bin/bash
set -e

echo "等待 MySQL 就绪..."

# 等待 MySQL 启动（最大等待 60 秒）
host="${DATABASE_HOST:-mysql}"
password="${DATABASE_PASSWORD:-devops123}"
max_wait=60
counter=0

until mysql -h "$host" -u root -p"$password" -e "SELECT 1" > /dev/null 2>&1; do
    counter=$((counter + 1))
    if [ $counter -eq $max_wait ]; then
        echo "MySQL 连接超时"
        exit 1
    fi
    echo "等待 MySQL 启动... ($counter/$max_wait)"
    sleep 1
done

echo "MySQL 已就绪"

# 执行数据库迁移
echo "执行数据库迁移..."
python manage.py migrate --noinput

# 创建管理员用户（如果不存在）
if [ -n "$ADMIN_USERNAME" ] && [ -n "$ADMIN_PASSWORD" ]; then
    echo "创建管理员用户..."
    python manage.py createsuperuser --noinput --username "$ADMIN_USERNAME" --email admin@example.com || true
fi

exec "$@"
