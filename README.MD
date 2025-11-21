
# ⚾ Baseball Stats Web Application

A full-stack Flask application that lets fans explore historical Major League Baseball data, track favorite teams, and manage users through an admin console.

---

## Core Features

| Area          | Highlights |
|---------------|------------|
| Public Pages  | • Home page with search<br>• Player profiles with season & career batting/pitching splits<br>• Team-season pages with standings and roster stats |
| Accounts      | • Registration & login (Flask-Login)<br>• Personal dashboard showing chosen favorite team |
| Admin Panel   | • Promote users<br>• Remove accounts |
| Data Layer    | • MySQL database seeded from the **Lahman** dataset<br>• SQLAlchemy ORM for high-level access<br>• Raw SQL for heavy stat queries where beneficial |
| UI / UX       | • Jinja2 templates & Bootstrap 5<br>• Responsive DataTables for sortable statistics |
| Dev-Friendly  | • Python 3.14 with virtual env<br>• Modular Blueprints (`pages`, `admin`) |


---

## Database setup

1. Import the baseball database
2. Run the **user.sql** file to create (or replace) the user table

---

## Admin User Creation

### Default Admin Credentials

username: admin
password: B@beRuth27!


To generate a different hashed password for the admin user, open a python shell and run this:
```python
from werkzeug.security import generate_password_hash
hashed = generate_password_hash("B@beRuth27!")
print(hashed)
```

Once ran, copy the output into the SQL statement below

Run the following SQL to create an admin user:

```sql
INSERT INTO user (username, password, email, favorite_team, user_type)
VALUES(
       'admin',
       'scrypt:32768:8:1$F4CZVtjHarkkYNEn$c3f3db32e06ab218172163c0795fc5b2fa9d15678545eb501f155c8d945d0097465f9037eee0dca81db82b50ef491cfb4c8430d54d8d3b0e51d3d2b1726868b5', -- MAKE SURE THIS IS HASSHED --
       'admin@example.com',
       'Detroit Tigers',
       'admin'
      );
```

## Quick Start

1. **Clone & enter the repo**

   ```bash
   git clone https://github.com/RadcliffeC/Baseball-Website.git
   cd baseball
   ```

2. **Create a virtual environment**

   ```bash
   python3.14 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application
    ```bash
   flask run
    ```

    ```bash
    python app.py
    ```
   
The application will be available at:
```bash
    http://localhost:5000/
```

## Configuration Notes

| Setting                | Where                                  |
|------------------------|----------------------------------------|
| `SECRET_KEY`           | Found in create_app                    |
| `SQLALCHEMY_DATABASE_URI` | Ditto                                  |
| Port / Host            | `flask run --host 0.0.0.0 --port 5000` |

---


## Acknowledgements

* [Sean Lahman Baseball Database](http://www.seanlahman.com/baseball-archive/statistics/)  
* Flask, SQLAlchemy, Bootstrap, DataTables