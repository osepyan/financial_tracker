financial_tracker/
├── .venv # Виртуальное окружение
├── creds # Директория для ключей и других чувствительных данных
│ └── gsheets
│ └── service_account_keys.json # Файл с ключом для Google Sheets API
├── financial_tracker # Основная директория пакета
│ ├── **init**.py # Инициализация пакета
│ ├── data_reader.py # Модуль для работы с Google Sheets
│ ├── data_processor.py # Модуль для обработки данных
│ ├── utils.py # Модуль с вспомогательными функциями, включая настройку логирования
│ └── visualizer.py # Модуль для визуализации данных
├── tests # Директория для тестов
│ └── **init**.py # Инициализация пакета тестов
├── app.py # Основной файл для запуска приложения Dash
├── main.py # Основной файл для демонстрации использования GoogleSheetsReader
├── poetry.lock # Lock-файл Poetry для управления зависимостями
├── pyproject.toml # Конфигурация Poetry
└── README.md # Описание проекта
