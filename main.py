import json
from cryptography.fernet import Fernet
from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder='template')

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/add_pwd_form")
def add_pwd_form():
    return render_template('add.html')

@app.route("/add_pwd", methods=["POST"])
def add_pwd():
    soft = request.form["soft"]
    pwd = request.form["pwd"]
    content = load()
    content[soft] = pwd
    save(content)
    return jsonify({"message": f"le mot de passe pour: {soft} a ete ajouter"})


@app.route("/get_pwd/<soft>", methods=["GET"])
def get_pwd(soft):
    try:
        return jsonify({"pwd": load()[soft]})
    except:
        return jsonify({"message": f"le service: {soft} nexiste pas"})


@app.route("/get_all_pwd", methods=["GET"])
def get_all_pwd():
    return jsonify({"content": load()})


def load():
    key = load_key()
    try:
        with open("db.json", "r") as file:
            content_crypts = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

    return {
        service: decrypt_password(content_crypt, key)
        for service, content_crypt in content_crypts.items()
    }


def encrypt_password(password, key):
    cipher_suite = Fernet(key)
    return cipher_suite.encrypt(password.encode())


def decrypt_password(encrypted_password, key):
    cipher_suite = Fernet(key)
    return cipher_suite.decrypt(encrypted_password).decode()


def save(content: dict):
    key = load_key()
    safe_dict = {}
    for service, pwd in content.items():
        safe_dict[service] = encrypt_password(pwd, key).decode()

    with open("db.json", "w") as file:
        json.dump(safe_dict, file, indent=2)


def load_key():
    try:
        return open("secret.key", "rb").read()
    except:
        key = Fernet.generate_key()
        with open("secret.key", "wb") as file:
            file.write(key)
        return key


def main():
    quit = False
    while not quit:
        choix = input(
            "1: ajouter un mot de passe\n2: aficher un mot de passe\n3: aficher tous les mot de passe\n4: quit\n>>> ")
        if choix == "1":
            add_pwd()
        elif choix == "2":
            get_pwd()
        elif choix == "3":
            get_all_pwd()
        elif choix == "4":
            quit = True


if __name__ == "__main__":
    app.run(debug=True)
    #main()
