#!/bin/bash

# SEO-парсер для анализа спроса на VPN по локациям
# Запуск: bash <(curl -sL https://raw.githubusercontent.com/grohotar/seo-parser/main/seo-parser.sh)

set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}  SEO-парсер для анализа VPN${NC}"
echo -e "${GREEN}=========================================${NC}"

# Создаём временную директорию
TEMP_DIR=$(mktemp -d)
echo -e "${YELLOW}📁 Создана временная директория: $TEMP_DIR${NC}"

# Функция очистки при выходе
cleanup() {
    echo -e "${YELLOW}🧹 Удаление временных файлов...${NC}"
    rm -rf "$TEMP_DIR"
    echo -e "${GREEN}✓ Временные файлы удалены${NC}"
}

# Регистрируем очистку при выходе
trap cleanup EXIT

cd "$TEMP_DIR"

# URL репозитория
REPO_URL="https://raw.githubusercontent.com/grohotar/seo-parser/main"

# Загружаем все файлы напрямую из GitHub
echo -e "${YELLOW}📥 Загрузка файлов из GitHub...${NC}"

# Файлы для загрузки
FILES=(
    "requirements.txt"
    "config.py"
    "query_builder.py"
    "google_trends_parser.py"
    "analyzer.py"
    "main.py"
)

for file in "${FILES[@]}"; do
    echo -e "${YELLOW}  → Загрузка: $file${NC}"
    if ! curl -sL -o "$file" "$REPO_URL/$file"; then
        echo -e "${RED}❌ Не удалось загрузить $file${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✓ Все файлы загружены${NC}"

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 не найден${NC}"
    exit 1
fi

# Проверяем и устанавливаем python3-venv если нужно
echo -e "${YELLOW}🔧 Проверка python3-venv...${NC}"
if ! python3 -m venv venv 2>/dev/null; then
    echo -e "${YELLOW}📦 Установка python3-venv...${NC}"
    if [ -x "$(command -v apt)" ]; then
        apt update && apt install -y python3.12-venv python3-dev
    elif [ -x "$(command -v yum)" ]; then
        yum install -y python3.12-venv python3-devel
    else
        echo -e "${RED}❌ Не удалось установить python3-venv${NC}"
        exit 1
    fi
    echo -e "${YELLOW}🔧 Повторное создание виртуального окружения...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate

# Устанавливаем зависимости
echo -e "${YELLOW}📦 Установка зависимостей...${NC}"
pip install -q -r requirements.txt

# Запускаем анализ
echo -e "${GREEN}✓ Запуск анализа...${NC}"
echo ""
python main.py

# Выход - вызовется cleanup() для удаления временных файлов
exit 0