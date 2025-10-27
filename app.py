from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def menu():
    return render_template('about.html')

@app.route('/leaderboards')
def leaderboards():
    return render_template('leaderboards.html')

@app.route('/about')
def about():
    return render_template('menu.html')

if __name__ == '__main__':
    app.run(debug=True)