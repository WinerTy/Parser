from typing import Dict, Tuple
from collections import defaultdict
import unicodedata
import re
import pymorphy3


class CategoryMatcher:
    def __init__(self, category_rules: Dict):
        self.category_rules = category_rules
        self.m = pymorphy3.MorphAnalyzer()
        self.normalized_rules = self._pre_normalize_rules(category_rules)

    def _pre_normalize_rules(self, rules: Dict) -> Dict:
        """Normalizes all keywords in the ruleset once during initialization."""
        normalized_rules = {}
        for category, subcategories in rules.items():
            normalized_subcategories = {}
            for subcategory, keywords in subcategories.items():
                normalized_keywords = [
                    self._preparate_phrase(kw) for kw in keywords if kw
                ]
                normalized_subcategories[subcategory] = [
                    kw for kw in normalized_keywords if kw
                ]
            normalized_rules[category] = normalized_subcategories
        return normalized_rules

    def _preparate_phrase(self, phrase: str) -> str:
        """Normalize string."""
        if not phrase:
            return ""

        phrase = str(phrase).lower()
        phrase = phrase.replace("-", " ")

        phrase = unicodedata.normalize("NFKD", phrase)
        phrase = re.sub(r"[^\w\s]", "", phrase)

        words = phrase.split()
        lemmatized_words = []
        for word in words:
            if not word:
                continue
            # Проверяем, есть ли self.m (на случай ошибки инициализации)
            if hasattr(self, "m") and self.m:
                parsed_word = self.m.parse(word)
                if parsed_word:
                    lemmatized_words.append(parsed_word[0].normal_form)
                else:
                    lemmatized_words.append(word)
            else:  # Если self.m не инициализирован, оставляем слово как есть
                lemmatized_words.append(word)

        phrase = " ".join(lemmatized_words)
        phrase = re.sub(r"\s+", " ", phrase).strip()
        return phrase

    def find_category(self, input_text: str) -> Tuple[str, str]:
        """
        Определяет категорию и подкатегорию для введенного текста.
        Баллы начисляются на основе общего количества вхождений всех
        ключевых слов подкатегории в нормализованном входном тексте.

        :param input_text: Входной текст для классификации.
        :return: Кортеж (категория, подкатегория). Если не найдено, возвращает ("Не определено", "Не определено").
        """
        normalized_input = self._preparate_phrase(input_text)

        if not normalized_input:
            return "Не определено", "Не определено"

        scores: defaultdict[Tuple[str, str], int] = defaultdict(int)

        for category, subcategories in self.normalized_rules.items():
            for subcategory, normalized_keywords in subcategories.items():
                current_subcategory_score = 0
                for normalized_keyword in normalized_keywords:
                    if normalized_keyword:  # Убедимся, что ключевое слово не пустое
                        occurrences = normalized_input.count(normalized_keyword)
                        current_subcategory_score += occurrences

                        # Опционально: можно добавить вес за длину ключевого слова,
                        # если это важно (например, более длинные совпадения важнее).
                        current_subcategory_score += occurrences * len(
                            normalized_keyword.split()
                        )

                if current_subcategory_score > 0:
                    scores[(category, subcategory)] = current_subcategory_score

        if not scores:
            return "Не определено", "Не определено"

        # Находим (категорию, подкатегорию) с максимальным счетом
        best_category_subcategory, max_score = max(
            scores.items(), key=lambda item: item[1]
        )

        # Обработка случаев с одинаковым максимальным счетом (опционально)
        tied_matches = [item for item, score in scores.items() if score == max_score]
        if len(tied_matches) > 1:
            # Можно добавить логику разрешения ничьих.
            # Например, выбрать ту, у которой больше уникальных совпавших ключевых слов,
            # или ту, у которой самое длинное совпавшее ключевое слово и т.д.
            # Пока что просто вернем первое из совпадений с максимальным счетом.
            # print(
            #     f"Warning: Tie detected for input '{input_text}'. Matches: {tied_matches} with score {max_score}."
            # )
            pass

        return best_category_subcategory
