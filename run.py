# run.py
from app import create_app
from config import Config

app = create_app()

if __name__ == '__main__':
    app.run(
        debug=Config.DEBUG,
        port=Config.PORT,
        # To reduce reload triggers, you can add:
        # extra_files=[],  # Don't watch extra files
        # use_reloader=True,  # Keep reloader but it will be less sensitive
    )