import os
from dotenv import load_dotenv
from rag_app import create_app

load_dotenv()
app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("FLASK_PORT", "5000")), debug=False)
