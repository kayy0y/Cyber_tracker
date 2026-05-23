# Cyber Compliance Tracker

## Tech Stack

| Layer    | Technology                          |
|----------|-------------------------------------|
| Backend  | Python + Flask                      |
| Database | MongoDB Atlas (free cloud)          |
| Frontend | HTML + Tailwind CDN + Vanilla JS    |
| Auth     | JWT (flask-jwt-extended) + bcrypt   |
| Deploy   | Render.com (free tier)              |

---

## Local Setup (Run on Your Computer)

### Step 1 — Install Python
Make sure Python 3.10 or above is installed.
Check with: `python --version`

### Step 2 — Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd cyber-compliance-tracker
```

### Step 3 — Create a virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 4 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 5 — Set up MongoDB Atlas

1. Go to https://mongodb.com/atlas and create a FREE account
2. Create a free cluster (M0 tier — no credit card needed)
3. Go to **Database Access** → Add a database user → set username and password
4. Go to **Network Access** → Add IP Address → Allow from anywhere → `0.0.0.0/0`
5. Click **Connect** → **Drivers** → Copy the connection string
   - It looks like: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/`

### Step 6 — Create your .env file
```bash
# Copy the example file
cp .env.example .env
```

Open `.env` in any text editor and fill it in:
```
MONGO_URI=mongodb+srv://youruser:yourpassword@cluster0.xxxxx.mongodb.net/cyber-compliance?retryWrites=true&w=majority
JWT_SECRET=any_long_random_string_you_make_up
```

### Step 7 — Run the app
```bash
python app.py
```

Open your browser at: **http://localhost:5000**

---

## First Login

1. Go to **http://localhost:5000/register**
2. Create an account with role **Admin**
3. You're in — start adding frameworks, tasks, and risks

---

## Deploy to Render.com (Put It on the Web)

### Step 1 — Push code to GitHub
Make sure your project is on GitHub (don't commit the `.env` file — `.gitignore` handles this).

### Step 2 — Create Render account
Go to https://render.com and sign up with your GitHub account.

### Step 3 — Create a new Web Service
1. Click **New → Web Service**
2. Connect your GitHub repository
3. Fill in these settings:
   - **Name**: cyber-compliance-tracker
   - **Root Directory**: (leave empty)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

### Step 4 — Add Environment Variables
In Render, go to **Environment** tab and add:
| Key | Value |
|-----|-------|
| `MONGO_URI` | Your MongoDB Atlas connection string |
| `JWT_SECRET` | Your secret key |

### Step 5 — Deploy
Click **Create Web Service**. Render will build and deploy your app.
You'll get a URL like: `https://cyber-compliance-tracker.onrender.com`

**Note**: Free tier on Render spins down after 15 minutes of inactivity. First load after that takes ~30 seconds. This is normal and fine for a demo.

---

## Project Structure

```
cyber-compliance-tracker/
├── app.py               ← Main Flask app, routes, and page endpoints
├── requirements.txt     ← Python packages to install
├── Procfile             ← Render deployment command
├── .env.example         ← Template for your .env file
├── config/
│   └── database.py      ← MongoDB connection
├── routes/
│   ├── auth.py          ← Register, login, JWT
│   ├── frameworks.py    ← Compliance frameworks CRUD
│   ├── tasks.py         ← Task management CRUD
│   ├── risks.py         ← Risk assessment CRUD
│   ├── dashboard.py     ← Stats aggregation
│   └── audit_logs.py    ← Activity log reader
└── templates/
    ├── base.html        ← Shared layout (sidebar + navbar)
    ├── login.html
    ├── register.html
    ├── dashboard.html   ← Charts + stats
    ├── frameworks.html
    ├── tasks.html
    ├── risks.html
    └── audit_logs.html
```
## Live Demo
