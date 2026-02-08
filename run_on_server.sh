#!/bin/bash

# Скрипт для запуска SEO-парсера на удаленном VPN-сервере через SSH
# Использование: ./run_on_server.sh user@server.com

set -e

if [ -z "$1" ]; then
    echo "Использование: $0 user@server.com"
    echo "Пример: $0 root@123.456.789.0"
    echo ""
    echo "Этот скрипт:"
    echo "1. Подключается к серверу по SSH"
    echo "2. Развертывает SEO-парсер"
    echo "3. Запускает анализ"
    echo "4. Показывает результаты в консоли"
    exit 1
fi

SERVER=$1
PROJECT_DIR="seo-parser"

echo "========================================="
echo "  Запуск SEO-парсера на $SERVER"
echo "========================================="

# Проверяем наличие SSH ключа
echo -e "\n[1/6] Проверка подключения..."
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes "$SERVER" echo "SSH OK" 2>/dev/null; then
    echo "❌ Ошибка: Не удалось подключиться к $SERVER"
    echo "Убедитесь что:"
    echo "  - Сервер доступен"
    echo "  - SSH ключ добавлен (ssh-copy-id $SERVER)"
    echo "  - Или будете вводить пароль вручную"
    exit 1
fi

echo "✓ SSH подключение работает"

# Копируем скрипт развертывания
echo -e "\n[2/6] Копирование скрипта развертывания..."
scp -q deploy.sh "$SERVER":~/
echo "✓ Скрипт скопирован"

# Запускаем развертывание
echo -e "\n[3/6] Развертывание на сервере..."
ssh "$SERVER" "bash ~/deploy.sh"
echo "✓ Развертывание завершено"

# Запускаем парсер
echo -e "\n[4/6] Запуск анализа..."
echo "Это займет несколько минут (около 2-3 минут для 30 стран)"
echo ""

ssh "$SERVER" "cd ~/$PROJECT_DIR && source venv/bin/activate && python main.py"

echo -e "\n========================================="
echo "  ✅ Анализ завершен!"
echo "========================================="
echo ""
echo "Результаты также доступны на сервере:"
echo "  SSH: $SERVER"
echo "  Команда: cd ~/$PROJECT_DIR && source venv/bin/activate && python main.py"
echo ""
echo "Для повторного запуска без развертывания:"
echo "  ssh $SERVER 'cd ~/$PROJECT_DIR && source venv/bin/activate && python main.py'"