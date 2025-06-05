from dotenv import load_dotenv
from ждp import create_app

load_dotenv()  # Load environment variables from .env file

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)