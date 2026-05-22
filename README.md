# ⚡ QuickShare

A lightweight Flask application for quickly uploading and sharing files over a local network using AWS S3 as the backend storage.

## Features

- 📤 **Easy File Upload** - Drag & drop or click to upload files
- 🔗 **Instant Sharing** - Generate shareable links instantly
- 📱 **QR Code Access** - Scan QR code to access from another device on the same WiFi
- 🔐 **Secure Downloads** - AWS S3 presigned URLs for secure, time-limited access
- 🗑️ **Delete Anytime** - Remove shared files with one click
- 🎨 **Beautiful UI** - Modern, responsive design

## Prerequisites

- Python 3.8+
- AWS Account with S3 bucket
- AWS credentials (Access Key ID & Secret Access Key)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Soumyadip-crypto-beep/-quickshare-.git
   cd quickshare
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env  # Or create .env file
   ```

   Add the following to your `.env` file:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_BUCKET_NAME=your_s3_bucket_name
   AWS_REGION=us-east-1
   PORT=5000
   DEBUG=false
   ```

## Running Locally

### On Linux/macOS
```bash
python app.py
```

### On Windows
```bash
run.bat
```

The app will start at `http://localhost:5000` and show your local network IP address.

## Deployment

### Heroku

1. Install the Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Set environment variables:
   ```bash
   heroku config:set AWS_ACCESS_KEY_ID=your_key
   heroku config:set AWS_SECRET_ACCESS_KEY=your_secret
   heroku config:set AWS_BUCKET_NAME=your_bucket
   heroku config:set AWS_REGION=us-east-1
   ```
5. Deploy: `git push heroku main`

### Other Platforms

The app includes a `Procfile` for deployment on platforms that support it (Heroku, Railway, etc.).

## API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home page with upload form |
| `/upload` | POST | Upload a file |
| `/share/<token>` | GET | Download page with presigned URL |
| `/download/<token>` | GET | Redirect to S3 presigned URL |
| `/delete/<token>` | POST | Delete a shared file |
| `/qr` | GET | Generate QR code for current IP |

## How It Works

1. User uploads a file via the web interface
2. File is uploaded to AWS S3 with a unique token
3. File metadata is stored in `files.json` in S3
4. Shareable link is generated with the token
5. Others can download via presigned URL (valid for 1 hour)
6. Files can be deleted, which removes from S3 and metadata

## File Structure

```
quickshare/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Deployment configuration
├── run.bat               # Windows startup script
├── .gitignore            # Git ignore rules
├── templates/
│   ├── index.html        # Upload page
│   └── download.html     # Download page
└── README.md             # This file
```

## Environment Variables

- `AWS_ACCESS_KEY_ID` - AWS IAM access key
- `AWS_SECRET_ACCESS_KEY` - AWS IAM secret key
- `AWS_BUCKET_NAME` - S3 bucket name
- `AWS_REGION` - AWS region (default: us-east-1)
- `PORT` - Port to run on (default: 5000)
- `DEBUG` - Enable debug mode (default: false)

## Security Notes

- Store AWS credentials securely in environment variables
- Don't commit `.env` file to version control
- Use IAM users with limited permissions for S3 access
- Presigned URLs expire after 1 hour by default
- Consider adding authentication for production use

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Contributing

Feel free to submit issues and enhancement requests!
