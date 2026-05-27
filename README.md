# Job Application Tracker

A Flask-based multi-user web application designed to help job seekers log, manage, and track their professional opportunities in one organized place. This project is built using raw SQL and session-based authentication to ensure complete data isolation between users.

---

## 📌 Overview
Applying for jobs and internships can quickly become chaotic. This application provides a centralized system where users can create accounts, log new job openings, track their progress through various hiring stages (Applied, Interview, Offer, Rejected), and manage their career pipeline efficiently.

---

## 🚀 Main Features
* **User Authentication:** Secure registration, login, and logout functionality using Flask sessions and cookies.
* **Multi-User Isolation:** Each user has a unique account. Users can only view, create, update, or delete their own application data.
* **Full CRUD Operations:** Complete management (Create, Read, Update, Delete) of job application records.
* **Dynamic Filtering:** Ability to filter application lists instantly based on hiring statuses.
* **Business Logic Tracking:** Structured around clear user stories mapped directly to a GitHub Projects Kanban board.

---

## 📁 Project Structure
```text
job-application-tracker/
│
├── app.py                 # Main Flask application and routing logic
├── database.py            # Raw SQL database connection and execution helpers
├── schema.sql             # Database schema definition (Tables setup)
├── requirements.txt       # Project dependencies
│
├── templates/             # HTML Templates
│   ├── base.html          # Base layout template
│   ├── login.html         # User login page
│   ├── register.html      # User registration page
│   ├── dashboard.html     # Main dashboard listing user-specific applications
│   └── application.html   # Form for adding and editing applications
│
└── tests/                 # Unit Testing
    └── test_logic.py      # Automated tests for core business logic functions
