import os
import uuid
import json
import socket
import io
import boto3
import qrcode
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from flask import Flask, render_template, request, redirect, url_for, abort, send_file
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)

PORT  = int(os.environ.get('PORT', 5000))
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'

AWS_BUCKET   = os.environ.get('AWS_BUCKET_NAME')
AWS_REGION   = os.environ.get('AWS_REGION', 'us-east-1')
DB_S3_KEY    = 'files.json'

s3 = boto3.client(
    's3',
    region_name=AWS_REGION,
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
)

# ── helpers ──────────────────────────────────────────────────────────────────

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.shutdown(socket.SHUT_RDWR)
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

def load_db():
    try:
        obj = s3.get_object(Bucket=AWS_BUCKET, Key=DB_S3_KEY)
        return json.loads(obj['Body'].read().decode('utf-8'))
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return {}
        raise

def save_db(data):
    s3.put_object(
        Bucket=AWS_BUCKET,
        Key=DB_S3_KEY,
        Body=json.dumps(data, indent=2).encode('utf-8'),
        ContentType='application/json'
    )

def s3_key(token, filename):
    return f"uploads/{token}_{filename}"

def presigned_url(token, filename, expires=3600):
    return s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': AWS_BUCKET, 'Key': s3_key(token, filename)},
        ExpiresIn=expires
    )

# ── routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    db = load_db()
    files = [{'name': name, 'token': token} for token, name in db.items()]
    network_url = f"http://{get_local_ip()}:{PORT}"
    return render_template('index.html', files=files, network_url=network_url)

@app.route('/qr')
def qr():
    url = f"http://{get_local_ip()}:{PORT}"
    img = qrcode.make(url)
    buf = io.BytesIO()
    try:
        img.save(buf, format='PNG')
        return send_file(io.BytesIO(buf.getvalue()), mimetype='image/png')
    finally:
        buf.close()

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file or file.filename == '':
        return redirect(url_for('index'))
    filename = secure_filename(file.filename)
    if not filename:
        return redirect(url_for('index'))
    token = uuid.uuid4().hex[:8]
    s3.upload_fileobj(file, AWS_BUCKET, s3_key(token, filename))
    db = load_db()
    db[token] = filename
    save_db(db)
    return redirect(url_for('index'))

@app.route('/share/<token>')
def share(token):
    filename = load_db().get(token)
    if not filename:
        abort(404)
    url = presigned_url(token, filename)
    return render_template('download.html', filename=filename, token=token, download_url=url)

@app.route('/download/<token>')
def download(token):
    filename = load_db().get(token)
    if not filename:
        abort(404)
    url = presigned_url(token, filename)
    return redirect(url)

@app.route('/delete/<token>', methods=['POST'])
def delete(token):
    db = load_db()
    filename = db.pop(token, None)
    if filename:
        save_db(db)
        try:
            s3.delete_object(Bucket=AWS_BUCKET, Key=s3_key(token, filename))
        except ClientError:
            pass
    return redirect(url_for('index'))

if __name__ == '__main__':
    print(f"\n  QuickShare running at: http://{get_local_ip()}:{PORT}\n")
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)