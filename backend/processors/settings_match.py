# Снижаем пороги для более мягкого сопоставления
BASE_RATIO = 60         # было 70 - снижаем для большей чувствительности
PARTIAL_RATIO = 70      # было 80
TOKEN_SET = 70          # было 80
JACCARD_MIN = 0.25      # было 0.35 - минимальное перекрытие токенов
ALLOW_EPISODE_PARTIAL = True
MAX_CANDIDATES = 12     # было 8 - увеличиваем количество кандидатов
ALLOW_CONTAINS = True
ALLOW_PARTIAL_WORDS = True  # Новая опция: разрешать частичное совпадение слов
