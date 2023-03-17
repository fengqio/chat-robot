from api.ding_server import app
from config import config

config_info = config.read_sys_config_path()

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=config_info.get("server", "port", fallback=8080))
