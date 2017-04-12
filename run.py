from wedding import app
import os

if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    port = int(os.environ.get('PORT', 33507))
    app.run(host='0.0.0.0', port=port)