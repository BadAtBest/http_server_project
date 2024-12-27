from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html") #serve the homepage

if __name__ == "__main__":
    print("Starting Flask app...") 
    app.run(host="0.0.0.0", port=8080)