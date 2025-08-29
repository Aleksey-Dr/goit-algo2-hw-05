import json
import re
import time
from hyperloglog import HyperLogLog
from tabulate import tabulate

def get_ip_addresses_from_log(file_path):
    """
    Витягує IP-адреси з лог-файлу.
    Ігнорує рядки, які не є валідним JSON.
    """
    ip_addresses = []
    ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                remote_addr = data.get('remote_addr')
                if remote_addr and ip_pattern.match(remote_addr):
                    ip_addresses.append(remote_addr)
            except json.JSONDecodeError:
                continue
    return ip_addresses

def count_unique_with_set(data):
    """
    Виконує точний підрахунок унікальних елементів за допомогою set.
    """
    unique_set = set()
    for item in data:
        unique_set.add(item)
    return len(unique_set)

def count_unique_with_hll(data, error_rate=0.01):
    """
    Виконує наближений підрахунок унікальних елементів за допомогою HyperLogLog.
    """
    hll = HyperLogLog(error_rate=error_rate)
    for item in data:
        hll.add(item)
    return len(hll)

def main():
    """
    Основна функція для порівняння методів та виведення результатів.
    """
    file_path = 'lms-stage-access.log'
    
    print("Завантаження даних...")
    ip_addresses = get_ip_addresses_from_log(file_path)
    total_ips = len(ip_addresses)
    print(f"Завантажено {total_ips} IP-адрес.\n")

    # Точний підрахунок з set
    start_time_set = time.time()
    unique_count_set = count_unique_with_set(ip_addresses)
    end_time_set = time.time()
    time_set = end_time_set - start_time_set

    # Наближений підрахунок з HyperLogLog
    start_time_hll = time.time()
    unique_count_hll = count_unique_with_hll(ip_addresses)
    end_time_hll = time.time()
    time_hll = end_time_hll - start_time_hll

    # Виведення результатів
    results = [
        ["Унікальні елементи", f"{unique_count_set:,.0f}", f"{unique_count_hll:,.0f}"],
        ["Час виконання (сек.)", f"{time_set:.4f}", f"{time_hll:.4f}"]
    ]

    headers = ["", "Точний підрахунок (Set)", "HyperLogLog"]
    print("Результати порівняння:")
    print(tabulate(results, headers=headers, tablefmt="grid"))
    
    # Розрахунок похибки HyperLogLog
    if unique_count_set > 0:
        error = abs(unique_count_set - unique_count_hll) / unique_count_set * 100
        print(f"\nАбсолютна похибка HyperLogLog: {unique_count_set - unique_count_hll:,.0f}")
        print(f"Відсоткова похибка HyperLogLog: {error:.2f}%")

if __name__ == "__main__":
    main()