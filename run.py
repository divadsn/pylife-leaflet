from waitress import serve
from pylife import app

if __name__ == "__main__":
    serve(app, host=app.config["HOST"], port=app.config["PORT"], threads=8)
