"""
Генератор вариаций поисковых запросов для каждой страны
"""


def generate_query_variations(country_name, country_data):
    """
    Генерирует все возможные вариации запросов для страны
    
    Args:
        country_name: Название страны на русском
        country_data: Словарь с данными страны
        
    Returns:
        list: Список всех вариаций запросов
    """
    name_en = country_data["name_en"]
    adjective_ru = country_data["adjective_ru"]
    adjective_en = country_data["adjective_en"]
    
    variations = []
    
    # Русские запросы с основным названием страны
    variations.append(f"впн {country_name}")
    variations.append(f"{country_name} впн")
    variations.append(f"{adjective_ru} впн")
    variations.append(f"впн для {country_name}")
    
    # Альтернативное название страны (если есть)
    if "name_ru_alt" in country_data:
        alt_name = country_data["name_ru_alt"]
        variations.append(f"впн {alt_name}")
        variations.append(f"{alt_name} впн")
        variations.append(f"впн для {alt_name}")
    
    # Краткая форма (если есть)
    if "name_ru_short" in country_data:
        variations.append(f"{country_data['name_ru_short']} впн")
    
    # Альтернативные формы прилагательных (если есть)
    if "adjective_ru_alt" in country_data:
        variations.append(f"{country_data['adjective_ru_alt']} впн")
    
    # Английские запросы
    variations.append(f"vpn {name_en}")
    variations.append(f"{name_en} vpn")
    variations.append(f"{adjective_en} vpn")
    variations.append(f"vpn for {name_en}")
    
    return variations


def generate_all_queries(countries_config):
    """
    Генерирует все запросы для всех стран
    
    Args:
        countries_config: Словарь с конфигурацией стран
        
    Returns:
        dict: {country_name: [query1, query2, ...]}
    """
    all_queries = {}
    
    for country_name, country_data in countries_config.items():
        variations = generate_query_variations(country_name, country_data)
        all_queries[country_name] = variations
        
    return all_queries


if __name__ == "__main__":
    from config import COUNTRIES
    
    # Тест генерации запросов
    all_queries = generate_all_queries(COUNTRIES)
    
    print("Пример запросов для Турции:")
    for query in all_queries["Турция"]:
        print(f"  - {query}")
    
    print(f"\nПример запросов для Армении:")
    for query in all_queries["Армения"]:
        print(f"  - {query}")
    
    print(f"\nПример запросов для Казахстана:")
    for query in all_queries["Казахстан"]:
        print(f"  - {query}")
    
    print(f"\nВсего стран: {len(all_queries)}")
    print(f"Всего вариаций запросов: {sum(len(v) for v in all_queries.values())}")