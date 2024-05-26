import json
from cryptography.fernet import Fernet
from flask import Flask, request, jsonify, render_template, redirect
import models
from database import SessionLocal, engine
from pydantic import BaseModel
from sqlalchemy.orm import Session
app = Flask(__name__, template_folder='template')
models.Base.metadata.create_all(bind=engine)

class Password(BaseModel):
    id: int
    name: str
    password: str


@app.route("/")
def home():
    return render_template('index.html', pwd="not found")


@app.route("/add_pwd_form")
def add_pwd_form():
    return render_template('add.html')


@app.route("/add_pwd", methods=["POST"])
def add_pwd():
    user = request.form["soft"]
    pwd = request.form["pwd"]
    savenewaccount(user, pwd)
    return redirect("/", code=302)


@app.route("/get_pwd", methods=["GET"])
def get_pwd():
    soft = request.args.get('soft')
    try:
        return render_template('index.html', pwd=load())
    except:
        return render_template("index.html", pwd="not found")

def load():
    key = load_key()
    try:
        db = SessionLocal()
        items = [i for i in db.query(models.PasswordDB).all()]
    finally:
        db.close()
    return {
        item.name: decrypt_password(item.password, key)
        for item in items
    }


def encrypt_password(password, key):
    cipher_suite = Fernet(key)
    return cipher_suite.encrypt(password.encode())


def decrypt_password(encrypted_password, key):
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(encrypted_password).decode()


def savenewaccount(service: str, password: str):
    try:
        db = SessionLocal()
        if len([i for i in db.query(models.PasswordDB).all()]) == 0:
            id = 1
        else:
            id = db.query(models.PasswordDB).order_by(models.PasswordDB.id.desc()).first().id + 1
        item = models.PasswordDB(id=id, name=service, password=password)
        key = load_key()
        item.password = encrypt_password(item.password, key).decode()
        db.add(item)
        db.commit()
    finally:
        db.close()


def load_key():
    try:
        return open("secret.key", "rb").read()
    except:
        key = Fernet.generate_key()
        with open("secret.key", "wb") as file:
            file.write(key)
        return key


if __name__ == "__main__":
    app.run(debug=True)
