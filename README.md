# Employee Management System with Face Recognition

A web-based **Employee Management System** developed using **Python, Django, OpenCV, Bootstrap, and SQLite**. The system provides secure role-based access for **Administrators** and **Employees**, along with **Face Recognition Attendance**, **Leave Management**, and **Employee Management**.

---

## 📌 Features

### 👨‍💼 Admin Module
- Secure Admin Login
- Dashboard
- Add New Employee
- Update Employee Details
- Delete Employee
- View Employee List
- Manage Leave Requests
  - Approve Leave
  - Reject Leave
- View Daily Attendance
- View Attendance History
- Export Attendance Report to **Excel**
- Export Attendance Report to **PDF**
- Manage Employee Records

---

### 👤 Employee Module
- Secure Employee Login
- View Personal Profile
- Face Recognition Attendance
  - Check-In
  - Check-Out
- View Attendance History
- Apply for Leave
- View Leave Status
- Dashboard

---

### 🎯 Face Recognition Module
- Employee Face Registration
- Dataset Generation
- Face Model Training
- Real-Time Face Recognition
- Automatic Attendance Marking
- Prevents Duplicate Attendance
- Check-In and Check-Out Support

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Backend |
| Django | Web Framework |
| OpenCV | Face Recognition |
| Bootstrap 5 | Frontend UI |
| HTML5 | Web Pages |
| CSS3 | Styling |
| JavaScript | Client-side Functionality |
| SQLite | Database |
| Pandas | Excel Export |
| ReportLab / FPDF | PDF Generation |

---

## 📂 Project Structure

```
employee_management_system/
│
├── accounts/
├── employees/
├── attendance/
├── leaves/
├── recognition/
├── templates/
├── static/
├── media/
├── db.sqlite3
├── manage.py
└── requirements.txt
```

---

## ⚙️ Installation

### 1. Clone Repository

```bash
git clone https://github.com/Anshchandnani/Python-Employee-Attendance-System-with-Face-Recognition.git
```

```bash
cd employee-management-system
```

---

### 2. Create Virtual Environment

Windows

```bash
python -m venv venv
```

Activate

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Apply Migrations

```bash
python manage.py makemigrations
```

```bash
python manage.py migrate
```

---

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

---

### 6. Run Development Server

```bash
python manage.py runserver
```

Open:

```
http://127.0.0.1:8000/
```

---

## 📸 Face Recognition Setup

### Capture Employee Images

Register employee images by login in to admin and then to employee page.

---

### Train the Face Recognition Model

Run the training script.

```bash
python manage.py train_model
```

*(Use the appropriate command if your project uses a custom training script.)*

---

### Start Face Recognition

Employees can start face recognition from their dashboard to:

- Check-In
- Check-Out

Attendance is automatically stored in the database.

---

## 📊 Attendance Features

- Daily Attendance
- Attendance History
- Check-In Time
- Check-Out Time
- Export Excel Report
- Export PDF Report

---

## 📝 Leave Management

Employee

- Apply for Leave
- View Leave Status

Administrator

- View Leave Requests
- Approve Leave
- Reject Leave

---

## 🔐 Authentication

The system supports two user roles:

### Admin

- Manage Employees
- Manage Leaves
- View Attendance
- Export Reports

### Employee

- View Profile
- Mark Attendance
- Apply Leave
- View Attendance History

---

## 📷 Screenshots

You can add screenshots here.
<img width="1920" height="1080" alt="Screenshot (357)" src="https://github.com/user-attachments/assets/d2f3cf72-44bf-4e94-a7a3-864ba8f2bff6" />
<img width="1920" height="1080" alt="Screenshot (358)" src="https://github.com/user-attachments/assets/95d4fa2f-7150-4da2-a973-f03a4842c987" />
<img width="1920" height="1080" alt="Screenshot (359)" src="https://github.com/user-attachments/assets/38cd246f-ae26-4d35-aef1-214182711c1a" />
<img width="1920" height="1080" alt="Screenshot (360)" src="https://github.com/user-attachments/assets/ceefa6fb-8c14-4fd0-993b-aa2965c60713" />



---

## 🚀 Future Improvements

- Email Notifications
- Face Liveness Detection
- Monthly Attendance Reports
- Payroll Module
- Department Management
- Shift Management
- REST API Integration
- Mobile Application
- Multi-Camera Support
- MySQL/PostgreSQL Support

---

## 📄 Requirements

In 'requirements.txt' file directly run
```
pip install -r requirements.txt
```

---

## 👨‍💻 Developed By

**Ansh Chandnani**

Diploma Engineering Student

Python | Django | OpenCV | Bootstrap

---

## 📜 License

This project is developed for educational and learning purposes.

Feel free to fork, modify, and improve the project.

---

## ⭐ Support

If you found this project useful:

- ⭐ Star this repository
- 🍴 Fork the repository
- 🐛 Report issues
- 💡 Suggest improvements

---

**Thank you for visiting this project!**
