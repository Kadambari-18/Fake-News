from flask import Flask, render_template, request, jsonify
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from googletrans import Translator
from newspaper import Article
import requests
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
 
app = Flask(__name__)
 
# -------------------- LOAD MODEL --------------------
try:
    print("Loading model...")
    model = load_model("fake_news_model.h5")
    print("Model loaded successfully")
except Exception as e:
    print("ERROR loading model:", e)
 
# -------------------- LOAD TOKENIZER --------------------
try:
    print("Loading tokenizer...")
    with open("tokenizer.pkl", "rb") as f:
        tokenizer = pickle.load(f)
    print("Tokenizer loaded successfully")
except Exception as e:
    print("ERROR loading tokenizer:", e)
 
translator = Translator()
history = []
max_len = 200
 
# -------------------- GMAIL CREDENTIALS --------------------
GMAIL_USER     = "kimayashendge@gmail.com"
GMAIL_PASSWORD = "hnet oqrm ynfz dokf"
 
# -------------------- NEWS API KEY --------------------
NEWS_API_KEY = "30ea1dc58266b98e3581126500a80eb7"
 
# -------------------- DATABASE INIT --------------------
def init_db():
    conn = sqlite3.connect('contact.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            message TEXT
        )
    ''')
    conn.commit()
    conn.close()
 
init_db()
 
# -------------------- HELPER: PREDICT TEXT --------------------
def predict_text(text):
    seq    = tokenizer.texts_to_sequences([text])
    padded = pad_sequences(seq, maxlen=max_len)
    score  = model.predict(padded)[0][0]
 
    print("RAW SCORE:", score)  # remove this line once everything works correctly
 
    # LOW score = FAKE, HIGH score = REAL (labels are flipped in your trained model)
    if score < 0.5:
        result     = "FAKE NEWS ❌"
        confidence = round((1 - float(score)) * 100, 2)
    else:
        result     = "REAL NEWS ✅"
        confidence = round(float(score) * 100, 2)
 
    return result, confidence
 
# -------------------- ROUTES --------------------
 
@app.route("/")
def home():
    return render_template("index.html")
 
@app.route("/home")
def home_page():
    return render_template("index.html")
 
@app.route("/detect")
def detect():
    return render_template("detect.html")
 
# -------------------- PREDICT (TEXT) --------------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        text = request.form["news"]
        lang = request.form.get("lang", "en")
 
        if lang != "en":
            text = translator.translate(text, dest="en").text
 
        result, confidence = predict_text(text)
 
        history.append({"text": text, "result": result, "confidence": confidence})
 
        return render_template("detect.html",
                               result=result,
                               confidence=confidence,
                               text=text)
 
    except Exception as e:
        print("PREDICTION ERROR:", e)
        return "Prediction error: " + str(e)
 
# -------------------- PREDICT (URL) --------------------
@app.route("/check_url", methods=["POST"])
def check_url():
    try:
        url = request.form["url"]
 
        article = Article(url)
        article.download()
        article.parse()
        text = article.text
 
        result, confidence = predict_text(text)
 
        history.append({"text": text, "result": result, "confidence": confidence})
 
        return render_template("detect.html",
                               result=result,
                               confidence=confidence,
                               text=text)
 
    except Exception as e:
        print("URL ERROR:", e)
        return "URL error: " + str(e)
 
# -------------------- HISTORY --------------------
@app.route("/history")
def show_history():
    return render_template("history.html", history=history)
 
# -------------------- ABOUT --------------------
@app.route("/about")
def about():
    return render_template("about.html")
 
# -------------------- CONTACT PAGE --------------------
@app.route('/contact')
def contact():
    return render_template('contact.html')
 
# -------------------- CONTACT SUBMIT --------------------
@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    try:
        name    = request.form['name']
        email   = request.form['email']
        message = request.form['message']
 
        print("FORM DATA:", name, email, message)
 
        # -------- SAVE TO DATABASE --------
        conn = sqlite3.connect('contact.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)",
                       (name, email, message))
        conn.commit()
        conn.close()
        print("Saved to DB successfully")
 
        # -------- SEND EMAIL --------
        msg = MIMEMultipart()
        msg['Subject'] = f"New Contact Message from {name}"
        msg['From']    = GMAIL_USER
        msg['To']      = GMAIL_USER
 
        body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
        msg.attach(MIMEText(body, 'plain'))
 
        print("Connecting to SMTP...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
 
        print("Logging in...")
        server.login(GMAIL_USER, GMAIL_PASSWORD)
 
        print("Sending email...")
        server.send_message(msg)
        server.quit()
 
        print("EMAIL SENT SUCCESSFULLY")
        return "success"
 
    except Exception as e:
        print("FULL ERROR:", e)
        return "error"
 
# -------------------- ADMIN VIEW --------------------
@app.route('/admin')
def admin():
    conn = sqlite3.connect('contact.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM contacts")
    data = cursor.fetchall()
    conn.close()
    return render_template("admin.html", data=data)
 
# -------------------- LIVE NEWS (HTML PAGE) --------------------
@app.route('/live_news')
def live_news():
    try:
        url      = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        data     = response.json()
        articles = data.get("articles", [])
 
        if not articles:
            return "No news found. Check API key in app.py."
 
        return render_template("live_news.html", articles=articles)
 
    except Exception as e:
        print("API ERROR:", e)
        return "Error loading news"
 
# -------------------- LIVE NEWS JSON (for detect page tab) --------------------
@app.route('/live_news_json')
def live_news_json():
    try:
        url      = f"https://newsapi.org/v2/top-headlines?country=in&pageSize=12&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        data     = response.json()
        articles = data.get("articles", [])
        return jsonify(articles)
 
    except Exception as e:
        print("LIVE NEWS JSON ERROR:", e)
        return jsonify([])
 
# -------------------- RUN APP --------------------
if __name__ == "__main__":
    print("Starting Flask Server...")
    app.run(host="0.0.0.0", port=5000, debug=True)
 