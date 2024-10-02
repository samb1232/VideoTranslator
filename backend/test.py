from flask import Flask, current_app, request, g

app = Flask(__name__)

@app.before_request
def before_request():
    g.user = get_current_user()

@app.route('/')
def index():
    user = g.user
    # Your code here
    return f"Hello, {user}!"

def get_current_user():
    # Your logic to get the current user
    return "Guest"

if __name__ == '__main__':
    app.run(debug=True)
