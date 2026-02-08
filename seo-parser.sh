#!/bin/bash

# SEO-парсер для анализа спроса на VPN по локациям
# Запуск: bash <(curl -sL https://github.com/grohotar/seo-parser/raw/main/seo-parser.sh)

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

# Создаём requirements.txt
cat > requirements.txt << 'EOF'
pytrends==4.9.2
requests==2.31.0
pandas>=2.0.0
EOF

# Создаём config.py
cat > config.py << 'EOFPYTHON'
"""
Конфигурация для парсера SEO-запросов
"""

# Список стран для анализа с их вариантами на русском и английском
COUNTRIES = {
    "Турция": {
        "name_en": "Turkey",
        "adjective_ru": "турецкий",
        "adjective_en": "turkish"
    },
    "Казахстан": {
        "name_en": "Kazakhstan",
        "adjective_ru": "казахский",
        "adjective_en": "kazakh"
    },
    "Германия": {
        "name_en": "Germany",
        "adjective_ru": "немецкий",
        "adjective_en": "german"
    },
    "США": {
        "name_en": "USA",
        "adjective_ru": "американский",
        "adjective_en": "american"
    },
    "Великобритания": {
        "name_en": "United Kingdom",
        "adjective_ru": "британский",
        "adjective_en": "british"
    },
    "Грузия": {
        "name_en": "Georgia",
        "adjective_ru": "грузинский",
        "adjective_en": "georgian"
    },
    "Армения": {
        "name_en": "Armenia",
        "adjective_ru": "армянский",
        "adjective_en": "armenian"
    },
    "Узбекистан": {
        "name_en": "Uzbekistan",
        "adjective_ru": "узбекский",
        "adjective_en": "uzbek"
    },
    "Польша": {
        "name_en": "Poland",
        "adjective_ru": "польский",
        "adjective_en": "polish"
    },
    "Финляндия": {
        "name_en": "Finland",
        "adjective_ru": "финский",
        "adjective_en": "finnish"
    },
    "Нидерланды": {
        "name_en": "Netherlands",
        "adjective_ru": "нидерландский",
        "adjective_en": "dutch"
    },
    "Кипр": {
        "name_en": "Cyprus",
        "adjective_ru": "кипрский",
        "adjective_en": "cypriot"
    },
    "Чехия": {
        "name_en": "Czech Republic",
        "adjective_ru": "чешский",
        "adjective_en": "czech"
    },
    "Япония": {
        "name_en": "Japan",
        "adjective_ru": "японский",
        "adjective_en": "japanese"
    },
    "Сингапур": {
        "name_en": "Singapore",
        "adjective_ru": "сингапурский",
        "adjective_en": "singaporean"
    },
    "Китай": {
        "name_en": "China",
        "adjective_ru": "китайский",
        "adjective_en": "chinese"
    },
    "Гонконг": {
        "name_en": "Hong Kong",
        "adjective_ru": "гонконгский",
        "adjective_en": "hong kong"
    },
    "Индия": {
        "name_en": "India",
        "adjective_ru": "индийский",
        "adjective_en": "indian"
    },
    "Израиль": {
        "name_en": "Israel",
        "adjective_ru": "израильский",
        "adjective_en": "israeli"
    },
    "Объединенные Арабские Эмираты": {
        "name_en": "UAE",
        "adjective_ru": "эмиратский",
        "adjective_en": "emirati"
    },
    "Швейцария": {
        "name_en": "Switzerland",
        "adjective_ru": "швейцарский",
        "adjective_en": "swiss"
    },
    "Швеция": {
        "name_en": "Sweden",
        "adjective_ru": "шведский",
        "adjective_en": "swedish"
    },
    "Канада": {
        "name_en": "Canada",
        "adjective_ru": "канадский",
        "adjective_en": "canadian"
    },
    "Австралия": {
        "name_en": "Australia",
        "adjective_ru": "австралийский",
        "adjective_en": "australian"
    },
    "Бразилия": {
        "name_en": "Brazil",
        "adjective_ru": "бразильский",
        "adjective_en": "brazilian"
    },
    "Аргентина": {
        "name_en": "Argentina",
        "adjective_ru": "аргентинский",
        "adjective_en": "argentinian"
    },
    "Мексика": {
        "name_en": "Mexico",
        "adjective_ru": "мексиканский",
        "adjective_en": "mexican"
    },
    "Южная Корея": {
        "name_en": "South Korea",
        "adjective_ru": "корейский",
        "adjective_en": "korean"
    },
    "Таиланд": {
        "name_en": "Thailand",
        "adjective_ru": "тайский",
        "adjective_en": "thai"
    },
    "Малайзия": {
        "name_en": "Malaysia",
        "adjective_ru": "малайзийский",
        "adjective_en": "malaysian"
    }
}

# Настройки периодов анализа
TIMEFRAMES = {
    "1_month": "today 1-m",
    "3_months": "today 3-m"
}

# Настройки геолокации (Россия)
GEO = "RU"

# Настройки категорий (IT/Интернет)
CATEGORY = 13

# Задержка между запросами (в секундах)
REQUEST_DELAY = 2
EOFPYTHON

# Создаём query_builder.py
cat > query_builder.py << 'EOFPYTHON'
"""
Генератор вариаций поисковых запросов для каждой страны
"""


def generate_query_variations(country_name, country_data):
    """
    Генерирует все возможные вариации запросов для страны
    """
    name_en = country_data["name_en"]
    adjective_ru = country_data["adjective_ru"]
    adjective_en = country_data["adjective_en"]
    
    variations = []
    
    # Русские запросы
    variations.append(f"впн {country_name}")
    variations.append(f"{country_name} впн")
    variations.append(f"{adjective_ru} впн")
    variations.append(f"впн для {country_name}")
    
    # Английские запросы
    variations.append(f"vpn {name_en}")
    variations.append(f"{name_en} vpn")
    variations.append(f"{adjective_en} vpn")
    variations.append(f"vpn for {name_en}")
    
    return variations


def generate_all_queries(countries_config):
    """
    Генерирует все запросы для всех стран
    """
    all_queries = {}
    
    for country_name, country_data in countries_config.items():
        variations = generate_query_variations(country_name, country_data)
        all_queries[country_name] = variations
        
    return all_queries
EOFPYTHON

# Создаём google_trends_parser.py
cat > google_trends_parser.py << 'EOFPYTHON'
"""
Парсер Google Trends для получения данных о поисковых запросах
"""
import time
from pytrends.request import TrendReq
import pandas as pd
from config import GEO, CATEGORY, REQUEST_DELAY, TIMEFRAMES


class GoogleTrendsParser:
    """Класс для парсинга данных из Google Trends"""
    
    def __init__(self, geo="RU", category=CATEGORY, delay=REQUEST_DELAY):
        self.geo = geo
        self.category = category
        self.delay = delay
        self.pytrends = TrendReq(hl='ru-RU', tz=180)
        self.request_count = 0
        
    def get_average_interest(self, queries, timeframe):
        """Получает средний интерес к запросам за период"""
        try:
            self.pytrends.build_payload(
                queries[:5],
                cat=self.category,
                timeframe=timeframe,
                geo=self.geo
            )
            data = self.pytrends.interest_over_time()
            
            self.request_count += 1
            if self.request_count > 1:
                time.sleep(self.delay)
                
            if data is None or data.empty:
                return None
            
            if 'isPartial' in data.columns:
                data = data.drop(columns=['isPartial'])
            
            averages = {}
            for query in queries[:5]:
                if query in data.columns:
                    averages[query] = data[query].mean()
                else:
                    averages[query] = 0
                    
            return averages
        except Exception as e:
            print(f"Ошибка при получении данных для {queries[:2]}: {e}")
            return None
    
    def parse_country_queries(self, country_name, queries, timeframes):
        """Парсит все запросы для одной страны за все периоды"""
        country_data = {
            "country": country_name,
            "queries": {}
        }
        
        for period_name, period_value in timeframes.items():
            averages = self.get_average_interest(queries, period_value)
            
            if averages:
                max_query = max(averages.items(), key=lambda x: x[1] if x[1] is not None else 0)
                
                period_data = {
                    "averages": averages,
                    "max_interest": max_query[1] if max_query[1] is not None else 0,
                    "top_query": max_query[0],
                    "all_queries": queries
                }
                country_data["queries"][period_name] = period_data
        
        return country_data
    
    def parse_all_countries(self, all_queries, timeframes):
        """Парсит данные для всех стран"""
        all_data = {}
        total_countries = len(all_queries)
        
        print(f"Начинаем парсинг {total_countries} стран...")
        print("=" * 60)
        
        for idx, (country_name, queries) in enumerate(all_queries.items(), 1):
            print(f"[{idx}/{total_countries}] Парсим {country_name}...")
            
            country_data = self.parse_country_queries(country_name, queries, timeframes)
            all_data[country_name] = country_data
            
            if idx < total_countries:
                time.sleep(self.delay)
        
        print("=" * 60)
        print(f"Парсинг завершен! Всего запросов: {self.request_count}")
        
        return all_data
EOFPYTHON

# Создаём analyzer.py
cat > analyzer.py << 'EOFPYTHON'
"""
Анализатор данных SEO-запросов
"""
from datetime import datetime


class SEOAnalyzer:
    """Класс для анализа данных SEO-запросов"""
    
    def __init__(self, all_data):
        self.all_data = all_data
        self.analyzed = {}
        
    def analyze_all_countries(self):
        """Анализирует данные по всем странам"""
        self.analyzed = {
            "countries": {},
            "ranking": {},
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        for country_name, country_data in self.all_data.items():
            self.analyzed["countries"][country_name] = self._analyze_country(country_data)
        
        self._create_rankings()
        return self.analyzed
    
    def _analyze_country(self, country_data):
        """Анализирует данные одной страны"""
        analysis = {
            "country": country_data["country"],
            "periods": {}
        }
        
        for period_name, period_data in country_data["queries"].items():
            if period_data and period_data.get("max_interest", 0) > 0:
                analysis["periods"][period_name] = {
                    "max_interest": period_data["max_interest"],
                    "top_query": period_data["top_query"],
                    "all_interests": period_data["averages"]
                }
        
        return analysis
    
    def _create_rankings(self):
        """Создает рейтинги стран по популярности"""
        ranking_3m = []
        ranking_1m = []
        
        for country_name, analysis in self.analyzed["countries"].items():
            if "3_months" in analysis["periods"]:
                ranking_3m.append({
                    "country": country_name,
                    "interest": analysis["periods"]["3_months"]["max_interest"],
                    "top_query": analysis["periods"]["3_months"]["top_query"]
                })
            
            if "1_month" in analysis["periods"]:
                ranking_1m.append({
                    "country": country_name,
                    "interest": analysis["periods"]["1_month"]["max_interest"],
                    "top_query": analysis["periods"]["1_month"]["top_query"]
                })
        
        ranking_3m.sort(key=lambda x: x["interest"], reverse=True)
        ranking_1m.sort(key=lambda x: x["interest"], reverse=True)
        
        self.analyzed["ranking"]["3_months"] = ranking_3m
        self.analyzed["ranking"]["1_month"] = ranking_1m
        
        self._calculate_trend()
    
    def _calculate_trend(self):
        """Вычисляет тренд (рост/падение) между периодами"""
        trends = []
        
        for country_name, analysis in self.analyzed["countries"].items():
            if "1_month" in analysis["periods"] and "3_months" in analysis["periods"]:
                interest_1m = analysis["periods"]["1_month"]["max_interest"]
                interest_3m = analysis["periods"]["3_months"]["max_interest"]
                
                if interest_3m > 0:
                    change_percent = ((interest_1m - interest_3m) / interest_3m) * 100
                else:
                    change_percent = 0
                
                trends.append({
                    "country": country_name,
                    "interest_1m": interest_1m,
                    "interest_3m": interest_3m,
                    "change_percent": change_percent
                })
        
        self.analyzed["trends"] = trends
    
    def get_top_countries(self, period="3_months", limit=20):
        """Возвращает топ стран по популярности"""
        return self.analyzed["ranking"].get(period, [])[:limit]
    
    def get_rising_countries(self, limit=10):
        """Возвращает страны с растущим спросом"""
        rising = [t for t in self.analyzed["trends"] if t["change_percent"] > 0]
        rising.sort(key=lambda x: x["change_percent"], reverse=True)
        return rising[:limit]
    
    def get_all_queries_interest(self, country_name, period="3_months"):
        """Возвращает интерес по всем вариациям запросов для страны"""
        if country_name not in self.analyzed["countries"]:
            return None
        
        period_data = self.analyzed["countries"][country_name]["periods"].get(period)
        if not period_data:
            return None
        
        interests = period_data.get("all_interests", {})
        result = [
            {"query": query, "interest": value if value is not None else 0}
            for query, value in interests.items()
        ]
        result.sort(key=lambda x: x["interest"], reverse=True)
        return result
EOFPYTHON

# Создаём main.py
cat > main.py << 'EOFPYTHON'
"""
Главный файл для запуска SEO-парсера
"""
from query_builder import generate_all_queries
from google_trends_parser import GoogleTrendsParser
from analyzer import SEOAnalyzer
from config import COUNTRIES, TIMEFRAMES


def print_header():
    print("=" * 80)
    print(" " * 20 + "АНАЛИЗ СПРОСА НА VPN ПО ЛОКАЦИЯМ")
    print(" " * 30 + "Россия | Google Trends")
    print("=" * 80)


def print_top_countries(analyzer):
    print("\n" + "=" * 80)
    print("ТОП-20 СТРАН ПО СПРОСУ (3 месяца)")
    print("=" * 80)
    
    top_3m = analyzer.get_top_countries("3_months", limit=20)
    
    print(f"{'№':<4} {'Страна':<20} {'Популярность':<15} {'Топ запрос'}")
    print("-" * 80)
    
    for idx, country in enumerate(top_3m, 1):
        print(f"{idx:<4} {country['country']:<20} {country['interest']:<15} {country['top_query']}")


def print_period_comparison(analyzer):
    print("\n" + "=" * 80)
    print("СРАВНЕНИЕ ПЕРИОДОВ: 1 месяц vs 3 месяца")
    print("=" * 80)
    
    top_3m = analyzer.get_top_countries("3_months", limit=10)
    top_1m = analyzer.get_top_countries("1_month", limit=10)
    
    print(f"{'Страна':<20} {'1 месяц':<15} {'3 месяца':<15} {'Изменение':<15} {'Тренд'}")
    print("-" * 80)
    
    top_1m_dict = {c["country"]: c["interest"] for c in top_1m}
    
    for country_3m in top_3m[:10]:
        country = country_3m["country"]
        interest_3m = country_3m["interest"]
        interest_1m = top_1m_dict.get(country, 0)
        
        if interest_3m > 0:
            change = ((interest_1m - interest_3m) / interest_3m) * 100
            change_str = f"{change:+.1f}%"
            
            if change > 5:
                trend = "↑↑↑"
            elif change > 0:
                trend = "↑↑"
            elif change < -5:
                trend = "↓↓↓"
            elif change < 0:
                trend = "↓↓"
            else:
                trend = "→"
        else:
            change_str = "N/A"
            trend = "→"
        
        print(f"{country:<20} {interest_1m:<15} {interest_3m:<15} {change_str:<15} {trend}")


def print_rising_countries(analyzer):
    print("\n" + "=" * 80)
    print("СТРАНЫ С РАСТУЩИМ СПРОСОМ (↑)")
    print("=" * 80)
    
    rising = analyzer.get_rising_countries(limit=10)
    
    print(f"{'Страна':<20} {'1 месяц':<15} {'3 месяца':<15} {'Рост':<15}")
    print("-" * 80)
    
    for country in rising:
        print(f"{country['country']:<20} {country['interest_1m']:<15} "
              f"{country['interest_3m']:<15} +{country['change_percent']:.1f}%")


def print_recommendations(analyzer):
    print("\n" + "=" * 80)
    print("РЕКОМЕНДАЦИИ ПО ПРИОРИТЕТУ ДОБАВЛЕНИЯ СЕРВЕРОВ")
    print("=" * 80)
    
    top_3m = analyzer.get_top_countries("3_months", limit=20)
    rising = analyzer.get_rising_countries(limit=10)
    
    print("\n🔥 КРИТИЧЕСКИЙ ПРИОРИТЕТ (высокий спрос + рост):")
    critical = []
    for country in rising:
        interest = next((c["interest"] for c in top_3m if c["country"] == country["country"]), 0)
        if interest > 50:
            critical.append((country["country"], interest, country["change_percent"]))
    
    if critical:
        for country, interest, change in sorted(critical, key=lambda x: -x[1]):
            print(f"  • {country:<20} (спрос: {interest}, рост: +{change:.1f}%)")
    else:
        print("  Нет стран с критическим приоритетом")
    
    print("\n✅ ВЫСОКИЙ ПРИОРИТЕТ (высокий спрос):")
    high = [c for c in top_3m[:10] if not any(r["country"] == c["country"] for r in critical)]
    for country in high:
        print(f"  • {country['country']:<20} (спрос: {country['interest']})")
    
    print("\n⚠️  СРЕДНИЙ ПРИОРИТЕТ:")
    medium = top_3m[10:20]
    for country in medium:
        print(f"  • {country['country']:<20} (спрос: {country['interest']})")


def print_timestamp(analyzer):
    print(f"\nВремя анализа: {analyzer.analyzed.get('timestamp', 'N/A')}")


def main():
    print_header()
    
    print("\nГенерация поисковых запросов...")
    all_queries = generate_all_queries(COUNTRIES)
    total_queries = sum(len(v) for v in all_queries.values())
    print(f"✓ Сгенерировано {len(all_queries)} стран с {total_queries} вариациями запросов")
    
    print("\nИнициализация парсера Google Trends...")
    parser = GoogleTrendsParser()
    print("✓ Парсер готов")
    
    print("-" * 80)
    all_data = parser.parse_all_countries(all_queries, TIMEFRAMES)
    
    print("\nАнализ полученных данных...")
    analyzer = SEOAnalyzer(all_data)
    analyzed = analyzer.analyze_all_countries()
    print(f"✓ Проанализировано {len(analyzed['countries'])} стран")
    
    print_top_countries(analyzer)
    print_period_comparison(analyzer)
    print_rising_countries(analyzer)
    print_recommendations(analyzer)
    print_timestamp(analyzer)
    
    print("\n" + "=" * 80)
    print("Анализ завершен!")
    print("=" * 80)


if __name__ == "__main__":
    main()
EOFPYTHON

# Проверяем Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 не найден${NC}"
    exit 1
fi

# Создаём виртуальное окружение
echo -e "${YELLOW}🔧 Создание виртуального окружения...${NC}"
python3 -m venv venv
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