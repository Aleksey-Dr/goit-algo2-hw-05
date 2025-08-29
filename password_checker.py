import hashlib
from typing import List, Dict

class BloomFilter:
    """
    Реалізація фільтра Блума.
    """

    def __init__(self, size: int, num_hashes: int):
        """
        Ініціалізує фільтр Блума.

        :param size: Розмір бітового масиву.
        :param num_hashes: Кількість хеш-функцій.
        """
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = [False] * size

    def _hash(self, item: str, seed: int) -> int:
        """
        Приватна хеш-функція для перетворення рядка на число.
        Використовує хеш SHA-256 для отримання стабільних хешів.

        :param item: Рядок, що хешується.
        :param seed: Зерно для унікальності хешу.
        :return: Хеш-значення в межах розміру масиву.
        """
        # Створення рядка з додаванням зерна для унікальності
        hashed_string = f"{item}{seed}".encode('utf-8')
        
        # Обчислення хешу SHA-256
        h = hashlib.sha256(hashed_string).hexdigest()
        
        # Перетворення хешу на ціле число та повернення значення за модулем розміру
        return int(h, 16) % self.size

    def add(self, item: str):
        """
        Додає елемент до фільтра.

        :param item: Елемент, що додається (пароль).
        """
        if not item or not isinstance(item, str):
            print(f"Попередження: Некоректний елемент '{item}' для додавання. Пропущено.")
            return

        for i in range(self.num_hashes):
            index = self._hash(item, i)
            self.bit_array[index] = True

    def contains(self, item: str) -> bool:
        """
        Перевіряє наявність елемента у фільтрі.
        
        Важливо: може давати хибнопозитивні результати.

        :param item: Елемент, що перевіряється (пароль).
        :return: True, якщо елемент, ймовірно, знаходиться у фільтрі, інакше False.
        """
        if not item or not isinstance(item, str):
            return False

        for i in range(self.num_hashes):
            index = self._hash(item, i)
            if not self.bit_array[index]:
                # Якщо хоча б один біт не встановлений, елемента точно немає
                return False
        
        # Якщо всі біти встановлені, елемент, ймовірно, є в фільтрі
        return True

def check_password_uniqueness(bloom_filter: BloomFilter, passwords: List[str]) -> Dict[str, str]:
    """
    Перевіряє унікальність списку паролів за допомогою фільтра Блума.

    :param bloom_filter: Екземпляр BloomFilter.
    :param passwords: Список паролів для перевірки.
    :return: Словник з результатами перевірки.
    """
    results = {}
    for password in passwords:
        if bloom_filter.contains(password):
            results[password] = "вже використаний"
        else:
            results[password] = "унікальний"
            # Додаємо новий унікальний пароль до фільтра для майбутніх перевірок
            bloom_filter.add(password)
    return results

if __name__ == "__main__":
    # Ініціалізація фільтра Блума
    # Розмір бітового масиву: 1000, кількість хеш-функцій: 3
    bloom = BloomFilter(size=1000, num_hashes=3)

    # Додавання існуючих паролів до фільтра
    existing_passwords = ["password123", "admin123", "qwerty123", ""] # Додано пустий рядок для тесту
    for password in existing_passwords:
        bloom.add(password)
        
    # Перевірка нових паролів
    new_passwords_to_check = ["password123", "newpassword", "admin123", "guest", None] # Додано None для тесту
    results = check_password_uniqueness(bloom, new_passwords_to_check)

    # Виведення результатів
    for password, status in results.items():
        print(f"Пароль '{password}' - {status}.")