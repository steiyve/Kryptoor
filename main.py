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
def home() -> str:
    """
    load home page
    :return:
    """
    return render_template('index.html', pwd="not found")


@app.route("/add_pwd_form")
def add_pwd_form() -> str:
    """
    load page to add password
    :return:
    """
    return render_template('add.html')


@app.route("/add_pwd", methods=["POST"])
def add_pwd():
    """
    get the form and save to the db
    :return:
    """
    user = request.form["soft"]
    pwd = request.form["pwd"]
    savenewaccount(user, pwd)
    return redirect("/", code=302)


@app.route("/get_pwd", methods=["GET"])
def get_pwd() -> str:
    """
    get a password
    :return:
    """
    soft = request.args.get('soft')
    try:
        return render_template('index.html', pwd=load(soft))
    except:
        return render_template("index.html", pwd="not found")

def load(soft: str) -> str:
    """
    load a password based on the service
    :param soft: software associer au password
    :return:
    """
    key = load_key()
    try:
        db = SessionLocal()
        return decrypt_password(db.query(models.PasswordDB).where(models.PasswordDB.soft == soft).first().password, key)
    finally:
        db.close()



def encrypt_password(password: str, key: bytes) -> bytes:
    """
    Encrypts the given password
    :param password: given password
    :param key: clef dencryption
    :return: mot de passe encrypter
    """
    cipher_suite = Fernet(key)
    return cipher_suite.encrypt(password.encode())


def decrypt_password(encrypted_password: str, key: bytes) -> str:
    """
    Decrypts the password from the db
    :param encrypted_password: le mot de passe encrypter
    :param key: la clef d'encryption
    :return: le mot de passe decrypter
    """
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(encrypted_password).decode()


def savenewaccount(soft: str, password: str) -> None:
    """
    add a new password to the database
    :param soft: service utiliser
    :param password: le mot de passe
    :return: rien
    """
    try:
        db = SessionLocal()
        if len([i for i in db.query(models.PasswordDB).all()]) == 0:
            id = 1
        else:
            id = db.query(models.PasswordDB).order_by(models.PasswordDB.id.desc()).first().id + 1
        item = models.PasswordDB(id=id, name=soft, password=password)
        key = load_key()
        item.password = encrypt_password(item.password, key).decode()
        db.add(item)
        db.commit()
    finally:
        db.close()


def load_key() -> bytes:
    """
    creer ou load une clef d'encryption
    :return: la clef d'encryption
    """
    try:
        return open("secret.key", "rb").read()
    except:
        key = Fernet.generate_key()
        with open("secret.key", "wb") as file:
            file.write(key)
        return key


if __name__ == "__main__":
    app.run(debug=True)
