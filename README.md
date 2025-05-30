
## How to run


1. Dowloand dependencies:
    2.1.For uv Package manager
    ```bash
    uv pip install .\requirements.txt
    ```
    2.2.For Pip(default) manager
    ```bash
    pip install -r .\requirements.txt
    ```

2. Setup .env file in ```./src/parser/```

```txt
APP_CONFIG__DB__URL=mysql+pymysql://<USER>:<PASSWORD>@<HOST>:<POST>/<DATABASE>
APP_CONFIG__BOT__TOKEN=BOT_TOKEN 
```

3. Go to ```./src/parser```

4. Run script
```bash
python main.py
```