# Dataset_preparation

## Описание

Программа для разметки датасетов для обучения моделей компьютерного зрения

Доступно: 
- Разметка для **YOLO-seg** при помощи **sam2**
- Разметка направлений
- Разметка для детектирования

TODO:
- Более удобный интерфейс, меньше работы с исходным кодом

## Зависимости

- **Windows**

- **python 3.12**

- Основные библиотеки:
    ```
    torch          2.7.1+cu128
    PyQt5          5.15.11
    opencv-python  4.12.0.88
    transformers   4.53.3
    ultralytics    8.3.169
    ```

## Установка

1. Создать и активировать виртуальное окружение:

    ```bash
    python -m venv .venv

    .venv\Scripts\Activate.ps1
    ```

    1.1. На Windows во время активации может возникнуть ошибка. Выполнить:

    ```bash
    Set-ExecutionPolicy Unrestricted -Scope Process # Разрешение в текущем терминале

    Set-ExecutionPolicy Unrestricted -Scope LocalMachine # Всегда
    ```

2. Установить зависимости через **pip**    

3. Склонировать репозиторий:

    ```bash
    git clone <ssh>
    ```

4. Зайти в директорию:

    ```bash
    cd Daraset_preparation
    ```

5. Склонировать репозиторий SAM2:

    ```bash
    git clone <sam2 ssh>
    ```

6. Установить SAM2:

    ```bash
    cd sam2
    pip install .
    cd ..
    ```

7. Запуск программы:

    ```bash
    python main.py
    ```

## Использование

[Docs](docs/README.md)



