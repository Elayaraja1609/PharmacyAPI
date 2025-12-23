# AWS Deployment Guide - Flask Backend

Complete step-by-step guide to deploy your Pharmacy API backend from GitHub to AWS.

## Prerequisites

- AWS Account (free tier available)
- GitHub repository: `Elayaraja1609/PharmacyAPI`
- MongoDB Atlas account (already set up)
- AWS CLI installed (optional, for advanced users)

---

## Option 1: AWS Elastic Beanstalk (Recommended - Easiest)

Elastic Beanstalk is the easiest way to deploy Python Flask apps on AWS.

### Step 1: Prepare Your Application

1. **Create `application.py` file** (if not exists):
   ```python
   # This file tells Elastic Beanstalk how to run your app
   from app import app

   if __name__ == "__main__":
       app.run()
   ```

2. **Create `.ebextensions/01_python.config`** (in root directory):
   ```yaml
   option_settings:
     aws:elasticbeanstalk:container:python:
       WSGIPath: application:app
   ```

3. **Create `.ebextensions/02_environment.config`**:
   ```yaml
   option_settings:
     aws:elasticbeanstalk:application:environment:
       MONGO_URI: "your-mongodb-connection-string"
       JWT_SECRET_KEY: "your-secret-key"
       FLASK_ENV: "production"
       FLASK_DEBUG: "False"
   ```

4. **Create `.ebignore`** (similar to .gitignore):
   ```
   venv/
   __pycache__/
   *.pyc
   .env
   .git/
   .gitignore
   ```

### Step 2: Install EB CLI

1. **Install Python 3.7+** (if not installed)

2. **Install EB CLI**:
   ```bash
   pip install awsebcli
   ```

3. **Verify installation**:
   ```bash
   eb --version
   ```

### Step 3: Initialize Elastic Beanstalk

1. **Navigate to your project root**:
   ```bash
   cd D:\Project\Pharmecy
   ```

2. **Initialize EB**:
   ```bash
   eb init
   ```

3. **Follow prompts**:
   - **Select region**: Choose closest to you (e.g., `us-east-1`)
   - **Application name**: `pharmacy-api` (or your choice)
   - **Platform**: Select `Python`
   - **Platform version**: Choose latest Python 3.9 or 3.10
   - **SSH**: Yes (for troubleshooting)
   - **Key pair**: Create new or select existing

### Step 4: Create Environment

1. **Create environment**:
   ```bash
   eb create pharmacy-api-env
   ```

2. **Wait for deployment** (5-10 minutes):
   - EB will create EC2 instance
   - Install dependencies
   - Deploy your app

### Step 5: Configure Environment Variables

1. **Go to AWS Console**:
   - Visit: https://console.aws.amazon.com/elasticbeanstalk

2. **Select your environment**: `pharmacy-api-env`

3. **Go to Configuration** → **Software** → **Edit**

4. **Add Environment Properties**:
   ```
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/pharmacy?retryWrites=true&w=majority
   JWT_SECRET_KEY=your-secret-key-here
   FLASK_ENV=production
   FLASK_DEBUG=False
   PORT=5000
   ```

5. **Save** and wait for environment update

### Step 6: Deploy from GitHub

**Option A: Deploy via EB CLI** (from local machine):

1. **Make sure code is committed**:
   ```bash
   git add .
   git commit -m "Ready for AWS deployment"
   git push origin main
   ```

2. **Deploy**:
   ```bash
   eb deploy
   ```

**Option B: Deploy from GitHub** (automatic):

1. **Go to Elastic Beanstalk Console**
2. **Select your environment**
3. **Go to Configuration** → **Deployment** → **Edit**
4. **Enable "Deploy from GitHub"**
5. **Connect GitHub account**
6. **Select repository**: `Elayaraja1609/PharmacyAPI`
7. **Branch**: `main`
8. **Save**

Now every push to GitHub will auto-deploy!

### Step 7: Get Your Application URL

1. **Go to Elastic Beanstalk Console**
2. **Select your environment**
3. **Copy the URL** (e.g., `pharmacy-api-env.eba-xxxxx.us-east-1.elasticbeanstalk.com`)

4. **Test your API**:
   ```
   https://pharmacy-api-env.eba-xxxxx.us-east-1.elasticbeanstalk.com/
   https://pharmacy-api-env.eba-xxxxx.us-east-1.elasticbeanstalk.com/api-docs
   ```

### Step 8: Configure Custom Domain (Optional)

1. **Go to Configuration** → **Load balancer** → **Edit**
2. **Add listener** for HTTPS (port 443)
3. **Add SSL certificate** (from AWS Certificate Manager)
4. **Update DNS** to point to EB URL

---

## Option 2: AWS EC2 (More Control)

For more control over your server.

### Step 1: Launch EC2 Instance

1. **Go to EC2 Console**: https://console.aws.amazon.com/ec2

2. **Launch Instance**:
   - **Name**: `pharmacy-api-server`
   - **AMI**: Amazon Linux 2023 (or Ubuntu 22.04)
   - **Instance Type**: t2.micro (free tier) or t3.small
   - **Key Pair**: Create new or select existing
   - **Security Group**: Create new
     - **Inbound Rules**:
       - SSH (22) from My IP
       - HTTP (80) from Anywhere
       - HTTPS (443) from Anywhere
       - Custom TCP (5000) from Anywhere (for Flask)

3. **Launch Instance**

### Step 2: Connect to EC2 Instance

1. **Get Public IP** from EC2 Console

2. **Connect via SSH**:
   ```bash
   ssh -i your-key.pem ec2-user@your-instance-ip
   ```

   (For Ubuntu, use `ubuntu` instead of `ec2-user`)

### Step 3: Install Dependencies

**For Amazon Linux**:
```bash
# Update system
sudo yum update -y

# Install Python 3.9
sudo yum install python3.9 python3.9-pip git -y

# Install nginx (reverse proxy)
sudo yum install nginx -y

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

**For Ubuntu**:
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9
sudo apt install python3.9 python3.9-pip python3.9-venv git nginx -y

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### Step 4: Clone Your Repository

```bash
# Create app directory
mkdir -p /var/www/pharmacy-api
cd /var/www/pharmacy-api

# Clone repository
sudo git clone https://github.com/Elayaraja1609/PharmacyAPI.git .

# Or clone to home directory first
cd ~
git clone https://github.com/Elayaraja1609/PharmacyAPI.git
sudo mv PharmacyAPI /var/www/pharmacy-api
cd /var/www/pharmacy-api
```

### Step 5: Set Up Python Environment

```bash
cd /var/www/pharmacy-api/backend

# Create virtual environment
python3.9 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 6: Configure Environment Variables

```bash
# Create .env file
sudo nano /var/www/pharmacy-api/backend/.env
```

**Add**:
```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/pharmacy?retryWrites=true&w=majority
JWT_SECRET_KEY=your-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
```

**Save**: `Ctrl+X`, then `Y`, then `Enter`

### Step 7: Create Systemd Service

```bash
# Create service file
sudo nano /etc/systemd/system/pharmacy-api.service
```

**Add**:
```ini
[Unit]
Description=Pharmacy API Flask Application
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/var/www/pharmacy-api/backend
Environment="PATH=/var/www/pharmacy-api/backend/venv/bin"
ExecStart=/var/www/pharmacy-api/backend/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Save and enable**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pharmacy-api
sudo systemctl start pharmacy-api

# Check status
sudo systemctl status pharmacy-api
```

### Step 8: Configure Nginx Reverse Proxy

```bash
# Create nginx config
sudo nano /etc/nginx/conf.d/pharmacy-api.conf
```

**Add**:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Or use EC2 public IP

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Test and reload nginx**:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Step 9: Configure Security Group

1. **Go to EC2 Console** → **Security Groups**
2. **Select your security group**
3. **Edit Inbound Rules**:
   - Allow HTTP (80) from `0.0.0.0/0`
   - Allow HTTPS (443) from `0.0.0.0/0`
   - Allow SSH (22) from your IP only

### Step 10: Test Your API

```bash
# Get your EC2 public IP from console
curl http://your-ec2-ip/
curl http://your-ec2-ip/api-docs
```

---

## Option 3: AWS App Runner (Containerized - Modern)

For containerized deployments (requires Dockerfile).

### Step 1: Create Dockerfile

Create `Dockerfile` in `backend/` directory:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
```

### Step 2: Create apprunner.yaml

Create `apprunner.yaml` in root:

```yaml
version: 1.0
runtime: python3
build:
  commands:
    build:
      - pip install -r backend/requirements.txt
run:
  runtime-version: 3.9
  command: python backend/app.py
  network:
    port: 5000
    env: PORT
  env:
    - name: MONGO_URI
      value: "your-mongodb-connection-string"
    - name: JWT_SECRET_KEY
      value: "your-secret-key"
    - name: FLASK_ENV
      value: "production"
```

### Step 3: Deploy via Console

1. **Go to App Runner Console**: https://console.aws.amazon.com/apprunner
2. **Create Service**
3. **Source**: GitHub
4. **Connect GitHub** and select repository
5. **Configure**:
   - **Build**: Automatic
   - **Deploy**: Automatic
6. **Create Service**

---

## MongoDB Atlas Configuration

### Whitelist AWS IPs

1. **Go to MongoDB Atlas** → **Network Access**
2. **Add IP Address**:
   - For Elastic Beanstalk: Add `0.0.0.0/0` (all IPs) or specific EB IPs
   - For EC2: Add your EC2 instance's public IP
   - For App Runner: Add `0.0.0.0/0` (all IPs)

---

## Cost Estimation

### Elastic Beanstalk:
- **Free Tier**: 750 hours/month for t2.micro
- **After Free Tier**: ~$15-30/month (t2.micro + data transfer)

### EC2:
- **Free Tier**: 750 hours/month for t2.micro
- **After Free Tier**: ~$10-15/month (t2.micro)

### App Runner:
- **No Free Tier**: ~$5-10/month (based on usage)

---

## Troubleshooting

### Elastic Beanstalk:

**Check logs**:
```bash
eb logs
```

**SSH into instance**:
```bash
eb ssh
```

**View environment health**: Check EB Console → Health

### EC2:

**Check application logs**:
```bash
sudo journalctl -u pharmacy-api -f
```

**Check nginx logs**:
```bash
sudo tail -f /var/log/nginx/error.log
```

**Restart service**:
```bash
sudo systemctl restart pharmacy-api
```

### Common Issues:

1. **Port 5000 not accessible**: Check security group rules
2. **MongoDB connection failed**: Whitelist AWS IPs in MongoDB Atlas
3. **502 Bad Gateway**: Check if Flask app is running (`sudo systemctl status pharmacy-api`)
4. **Import errors**: Check Python version and dependencies

---

## Quick Comparison

| Option | Difficulty | Cost | Best For |
|--------|-----------|------|----------|
| **Elastic Beanstalk** | ⭐ Easy | $$ | Quick deployment |
| **EC2** | ⭐⭐ Medium | $ | Full control |
| **App Runner** | ⭐⭐ Medium | $$ | Modern apps |

---

## Recommended: Elastic Beanstalk

**Why?**
- ✅ Easiest to set up
- ✅ Automatic scaling
- ✅ Built-in load balancing
- ✅ Easy GitHub integration
- ✅ Free tier available

**Steps Summary**:
1. Install EB CLI
2. Run `eb init`
3. Run `eb create`
4. Configure environment variables
5. Deploy: `eb deploy` or connect GitHub

---

## Next Steps After Deployment

1. ✅ Test all API endpoints
2. ✅ Set up custom domain (optional)
3. ✅ Configure SSL certificate (HTTPS)
4. ✅ Set up monitoring/alerting
5. ✅ Configure auto-scaling (if needed)

---

## Support

- **AWS Documentation**: https://docs.aws.amazon.com
- **Elastic Beanstalk Docs**: https://docs.aws.amazon.com/elasticbeanstalk
- **EC2 Documentation**: https://docs.aws.amazon.com/ec2

Good luck with your deployment! 🚀

