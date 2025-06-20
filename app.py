from flask import Flask, render_template, request, send_file
from cryptography.fernet import Fernet
import hashlib, base64, os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_key(password):
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

@app.route('/', methods=['GET', 'POST'])
def index():
    result = ""
    if request.method == 'POST':
        file = request.files['file']
        password = request.form['password']
        action = request.form['action']
        filename = file.filename
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        key = get_key(password)
        fernet = Fernet(key)

        with open(filepath, 'rb') as f:
            data = f.read()

        try:
            if action == 'encrypt':
                result_data = fernet.encrypt(data)
                out_name = filename + ".enc"
            elif action == 'decrypt':
                result_data = fernet.decrypt(data)
                out_name = filename.replace(".enc", ".dec")
            out_path = os.path.join(UPLOAD_FOLDER, out_name)
            with open(out_path, 'wb') as f:
                f.write(result_data)
            return send_file(out_path, as_attachment=True)
        except Exception as e:
            result = f"Fel: {str(e)}"
    return render_template('index.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)