"""
Главный файл для запуска SEO-парсера
Анализирует спрос на VPN по локациям в России
"""
from query_builder import generate_all_queries
from google_trends_parser import GoogleTrendsParser
from analyzer import SEOAnalyzer
from config import COUNTRIES, TIMEFRAMES


def print_header():
    """Выводит заголовок"""
    print("=" * 80)
    print(" " * 20 + "АНАЛИЗ СПРОСА НА VPN ПО ЛОКАЦИЯМ")
    print(" " * 30 + "Россия | Google Trends")
    print("=" * 80)


def print_separator():
    """Выводит разделитель"""
    print("-" * 80)


def print_top_countries(analyzer):
    """Выводит топ стран по популярности"""
    print("\n" + "=" * 80)
    print("ТОП-20 СТРАН ПО СПРОСУ (3 месяца)")
    print("=" * 80)
    
    top_3m = analyzer.get_top_countries("3_months", limit=20)
    
    print(f"{'№':<4} {'Страна':<20} {'Кол-во запросов':<15} {'Популярность'}")
    print("-" * 80)
    
    for idx, country in enumerate(top_3m, 1):
        query_count = analyzer.get_query_count(country["country"])
        interest = country["interest"]
        print(f"{idx:<4} {country['country']:<20} {query_count:<15} {interest:.2f}")


def print_period_comparison(analyzer):
    """Выводит сравнение периодов"""
    print("\n" + "=" * 80)
    print("СРАВНЕНИЕ ПЕРИОДОВ: 1 месяц vs 3 месяца")
    print("=" * 80)
    
    top_3m = analyzer.get_top_countries("3_months", limit=10)
    top_1m = analyzer.get_top_countries("1_month", limit=10)
    
    print(f"{'Страна':<20} {'1 месяц':<15} {'3 месяца':<15} {'Изменение':<15} {'Тренд'}")
    print("-" * 80)
    
    # Создаем словарь для быстрого доступа
    top_1m_dict = {c["country"]: c["interest"] for c in top_1m}
    
    for country_3m in top_3m[:10]:
        country = country_3m["country"]
        interest_3m = country_3m["interest"]
        interest_1m = top_1m_dict.get(country, 0)
        
        if interest_3m > 0 and interest_1m > 0:
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
            
            print(f"{country:<20} {interest_1m:<15.2f} {interest_3m:<15.2f} {change_str:<15} {trend}")


def print_rising_countries(analyzer):
    """Выводит страны с растущим спросом"""
    print("\n" + "=" * 80)
    print("СТРАНЫ С РАСТУЩИМ СПРОСОМ (↑)")
    print("=" * 80)
    
    rising = analyzer.get_rising_countries(limit=10)
    
    print(f"{'Страна':<20} {'1 месяц':<15} {'3 месяца':<15} {'Рост':<15}")
    print("-" * 80)
    
    for country in rising:
        print(f"{country['country']:<20} {country['interest_1m']:<15} "
              f"{country['interest_3m']:<15} +{country['change_percent']:.1f}%")


def print_falling_countries(analyzer):
    """Выводит страны с падающим спросом"""
    print("\n" + "=" * 80)
    print("СТРАНЫ С ПАДАЮЩИМ СПРОСОМ (↓)")
    print("=" * 80)
    
    falling = analyzer.get_falling_countries(limit=10)
    
    if falling:
        print(f"{'Страна':<20} {'1 месяц':<15} {'3 месяца':<15} {'Падение':<15}")
        print("-" * 80)
        
        for country in falling:
            print(f"{country['country']:<20} {country['interest_1m']:<15} "
                  f"{country['interest_3m']:<15} {country['change_percent']:.1f}%")
    else:
        print("Нет данных о падающем спросе")


def print_country_details(analyzer, country_name, period="3_months"):
    """Выводит детальную информацию по стране"""
    print("\n" + "=" * 80)
    print(f"ДЕТАЛИ ПО СТРАНЕ: {country_name.upper()} ({period})")
    print("=" * 80)
    
    # Все запросы с интересом
    queries = analyzer.get_all_queries_interest(country_name, period)
    
    if queries:
        # Фильтруем только запросы с положительным интересом
        valid_queries = [q for q in queries if q['interest'] > 0]
        
        if valid_queries:
            print("\nТОП ЗАПРОСОВ:")
            for i, query in enumerate(valid_queries[:8], 1):
                print(f"  {i}. {query['query']:30} - {query['interest']:.2f}")
        else:
            print("\n❌ Нет валидных запросов (все с нулевым интересом)")
        
        # Связанные запросы
        related = analyzer.get_related_queries(country_name, period, limit=5)
        
        if related and (related["top"] or related["rising"]):
            print("\nСВЯЗАННЫЕ ЗАПРОСЫ:")
            
            if related["top"]:
                print("  Популярные:")
                for q in related["top"][:5]:
                    print(f"    • {q['query']}")
            
            if related["rising"]:
                print("  Растущие:")
                for q in related["rising"][:5]:
                    print(f"    • {q['query']}")
    else:
        print(f"Нет данных для {country_name}")


def print_recommendations(analyzer):
    """Выводит рекомендации по добавлению серверов"""
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
    """Выводит время анализа"""
    print(f"\nВремя анализа: {analyzer.analyzed.get('timestamp', 'N/A')}")


def main():
    """Главная функция"""
    print_header()
    
    # Генерируем запросы
    print("\nГенерация поисковых запросов...")
    all_queries = generate_all_queries(COUNTRIES)
    total_queries = sum(len(v) for v in all_queries.values())
    print(f"✓ Сгенерировано {len(all_queries)} стран с {total_queries} вариациями запросов")
    
    # Создаем парсер
    print("\nИнициализация парсера Google Trends...")
    parser = GoogleTrendsParser()
    print("✓ Парсер готов")
    
    # Парсим данные
    print_separator()
    all_data = parser.parse_all_countries(all_queries, TIMEFRAMES)
    
    # Удаляем страны без данных (None)
    valid_data = {k: v for k, v in all_data.items() if v is not None}
    invalid_countries = [k for k, v in all_data.items() if v is None]
    
    if invalid_countries:
        print(f"\n⚠️  Не удалось получить данные для следующих стран:")
        for country in invalid_countries:
            print(f"    • {country}")
    
    # Анализируем только валидные данные
    print("\nАнализ полученных данных...")
    analyzer = SEOAnalyzer(valid_data, all_queries)
    analyzed = analyzer.analyze_all_countries()
    print(f"✓ Проанализировано {len(analyzed['countries'])} стран с валидными данными")
    
    # Выводим результаты
    print_top_countries(analyzer)
    print_period_comparison(analyzer)
    print_rising_countries(analyzer)
    print_falling_countries(analyzer)
    
    # Детали по топ-3 странам
    top_3 = analyzer.get_top_countries("3_months", limit=3)
    for country in top_3:
        print_country_details(analyzer, country["country"])
    
    # Рекомендации
    print_recommendations(analyzer)
    
    # Таймстамп
    print_timestamp(analyzer)
    
    print("\n" + "=" * 80)
    print("Анализ завершен!")
    print("=" * 80)


if __name__ == "__main__":
    main()