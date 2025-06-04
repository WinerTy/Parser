# Подготовка к запуску


1. Клонирование репозитория 
    ```bash
     git clone --depth=1 https://github.com/WinerTy/Parser.git
     ```

2. Настройка окружения
    - Зайти в директорию проетка 
    ```bash
        cd Parser 
    ```
    - Создать в ней файл .env со своими данными 
    ```bash
    echo -e "APP_CONFIG__DB__URL=mysql+pymysql://<USER>:<PASSWORD>@<HOST>:<POST>/<DATABASE>\nAPP_CONFIG__BOT__TOKEN=<BOT_TOKEN>" > .env
    ```

    - Установить Docker (Если нету). [**Документация по установке**](https://docs.docker.com/engine/install/ubuntu/)

3. Запуск контейнера 
    - Сборка, Название сборки может быть любое наприме: parser
    ```bash
    docker build -t <Название сборки> .
    ```

    - Запуск 
    ```bash
    docker run <Название сборки>
    ```
    - Если нужно запустить в фоновом режиме 
    ```bash
    docker run -d <Название сборки>
    ```

    - Проверить что контейнер запустился можно через
    ```bash
    docker ps -a
    ```
    В результате будет выдана информация по всем активным контейнерам (conteiner id, image, command, created, status и т.д)
