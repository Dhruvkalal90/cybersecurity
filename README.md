# 🛡️ CyberBridge

**CyberBridge** is a Django-based cybersecurity collaboration platform that connects **businesses** with **ethical hackers (CEH-certified or skilled security researchers)** to solve real-world security problems.
The system provides a structured environment for vulnerability reporting, awareness sessions, blogs, payments, and managed interactions between organizations and security professionals.

---

## 🚀 Project Overview

CyberBridge enables:

* 🔐 Businesses to post security requirements and manage threats
* 🧑‍💻 Ethical hackers to offer services and expertise
* 📝 Blogs & awareness sessions for cybersecurity education
* 💳 Secure payment & invoice management
* 📊 Admin monitoring and complaint handling
* 🧾 Audit logging for transparency

The platform uses **role-based access control** with three primary roles:

* Business
* Hacker
* Admin

---

## 🏗️ Tech Stack

* **Backend:** Django
* **Database:** SQLite (default, configurable)
* **Frontend:** HTML, CSS, Bootstrap
* **Payments:** Razorpay
* **Auth:** Custom Django User Model
* **Python:** 3.10+ recommended

---

## 📦 Clone the Repository

```bash
git clone https://github.com/Dhruvkalal90/cybersecurity.git
cd cybersecurity
```

---

## 🧪 Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 📥 Install Requirements

If `requirements.txt` exists:

```bash
pip install -r requirements.txt
```

If not, install core dependencies manually:

```bash
pip install django djangorestframework pillow razorpay python-dotenv crispy-bootstrap5
```

Then generate requirements for future use:

```bash
pip freeze > requirements.txt
```

---

## 🗄️ Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 👤 Create Superuser

```bash
python manage.py createsuperuser
```

Follow prompts for email and password.

---

## ▶️ Run Development Server

```bash
python manage.py runserver
```

Open in browser:

```
http://127.0.0.1:8000/
```

Admin panel:

```
http://127.0.0.1:8000/admin
```

---

## 📁 Project Structure

```
CyberBridge/
│
├── manage.py
├── requirements.txt
├── db.sqlite3
│
├── apps/
│   ├── users
│   ├── blogs
│   ├── complaints
│   ├── payments
│   └── awareness
│
├── templates/
├── static/
└── venv/   (not committed)
```

---

## 🔒 Environment Variables (optional)

Create `.env` file in root:

```
SECRET_KEY=your_secret_key
DEBUG=True
RAZORPAY_KEY=your_key
RAZORPAY_SECRET=your_secret
```

---

## 🧠 Development Notes

* Do **not** commit `venv/`
* Always update dependencies:

  ```bash
  pip freeze > requirements.txt
  ```
* Use role-based dashboards for testing

---

## 🤝 Contributing

1. Fork repo
2. Create branch
3. Commit changes
4. Open PR

---

## 📜 License

This project is for academic and development purposes.
Modify and use as needed.

---

## 👨‍💻 Maintainer

**CyberBridge Team**
Cybersecurity Collaboration Platform
