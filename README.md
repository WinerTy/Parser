
## How to run

1. Setup .env file

```txt
APP_CONFIG__DB__URL=mysql+pymysql://<USER>:<PASSWORD>@<HOST>:<POST>/<DATABASE>
APP_CONFIG__BOT__TOKEN=BOT_TOKEN 
```

2. Dowloand dependencies 
```uv pip install .\requirements.txt``` - For uv Package manager
```pip install -r .\requirements.txt``` - For Pip(default) manager

3. Go to ```./src/parser```

4. Run script
```bash
python main.py
```