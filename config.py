"""
Конфигурация для парсера SEO-запросов
"""

# Список стран для анализа с их вариантами на русском и английском
COUNTRIES = {
    "Турция": {
        "name_en": "Turkey",
        "adjective_ru": "турецкий",
        "adjective_ru_alt": "турецкая",
        "adjective_en": "turkish"
    },
    "Казахстан": {
        "name_en": "Kazakhstan",
        "adjective_ru": "казахский",
        "adjective_ru_alt": "казахстанский",
        "adjective_en": "kazakh"
    },
    "Германия": {
        "name_en": "Germany",
        "adjective_ru": "немецкий",
        "adjective_ru_alt": "германская",
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
        "adjective_ru_alt": "грузинская",
        "adjective_en": "georgian"
    },
    "Армения": {
        "name_en": "Armenia",
        "adjective_ru": "армянский",
        "adjective_ru_alt": "армянская",
        "adjective_en": "armenian"
    },
    "Узбекистан": {
        "name_en": "Uzbekistan",
        "adjective_ru": "узбекский",
        "adjective_ru_alt": "узбекская",
        "adjective_en": "uzbek"
    },
    "Польша": {
        "name_en": "Poland",
        "adjective_ru": "польский",
        "adjective_ru_alt": "польская",
        "adjective_en": "polish"
    },
    "Финляндия": {
        "name_en": "Finland",
        "adjective_ru": "финский",
        "adjective_ru_alt": "финская",
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
        "name_ru_short": "оаэ",
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

# Задержка между запросами (в секундах) чтобы не заблокировали
REQUEST_DELAY = 2