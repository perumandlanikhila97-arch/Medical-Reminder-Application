# 💊 Medical Reminder Application

A lightweight desktop application that helps users manage medication schedules by importing prescriptions and automatically generating personalized medicine reminders.

Built with **Python** and **Tkinter**, the application combines prescription uploads, automated scheduling, reminder notifications, medication tracking, and schedule exports in a simple, local-first solution.

---

## 📌 Features

### 📄 Prescription Import

Import medication details directly from prescription files.

Supported formats:

* **CSV Files**

  * Columns: `name`, `dose`, `times`, `notes`
  * Multiple times can be separated using commas or semicolons.

* **TXT Files**

  * Format:

    ```
    MedicineName, Dose, Times, OptionalNotes
    ```
  * Multiple times can be separated using commas or semicolons.

---

### ⏰ Automated Medication Scheduling

* Automatically generates a daily medication timetable from imported prescriptions.
* Displays all scheduled doses in an easy-to-read interface.
* Eliminates the need for manual schedule creation.

---

### 🔔 Smart Reminder System

The built-in background scheduler continuously monitors upcoming medication times and triggers reminders when required.

Available reminder actions:

* ✅ Mark as Taken
* ⏳ Snooze (10 Minutes)
* ❌ Skip Dose

---

### ✏️ Manual Medication Management

Manage medications directly through the application interface.

Users can:

* Add medicines
* Edit existing schedules
* Delete medications
* Update dosage information
* Modify reminder times

---

### 💾 Persistent Data Storage

All medication data is stored locally.

Files generated:

| File               | Purpose                                          |
| ------------------ | ------------------------------------------------ |
| `medicines.json`   | Stores medication schedules and details          |
| `medicine_log.csv` | Records medication activity and reminder history |

---

### 📊 Schedule Export

Export generated schedules to CSV format for:

* Printing
* Sharing with caregivers
* Personal record keeping

---

### 🔒 Local-First Design

* No internet connection required
* No external services or APIs
* All information remains on the user's device

---

## 🚀 Getting Started

### Prerequisites

* Python 3.x

### Run the Application

```bash
python medicine_reminder_gui_with_upload.py
```

### Basic Workflow

1. Launch the application.
2. Upload a prescription file or manually add medications.
3. Start the reminder scheduler.
4. Receive notifications at scheduled times.
5. Track medication history through the activity log.
6. Export schedules when needed.

---

## 👥 Intended Users

This application is suitable for:

* Individuals managing daily medications
* Family members managing prescriptions for loved ones
* Caregivers
* Small clinics requiring a simple medication reminder solution

---

## 🛠️ Technology Stack

* Python 3
* Tkinter (GUI Framework)
* Threading (Background Scheduler)
* JSON (Data Storage)
* CSV (Logging & Export)

---

## ⚙️ Configuration

For testing purposes, reminder polling frequency can be adjusted by modifying:

```python
CHECK_INTERVAL_SECONDS
```

Lower values provide faster reminder detection during development and testing.

---

## 📈 Future Enhancements

Potential improvements include:

* OCR-based prescription scanning
* Mobile application support
* Email and SMS notifications
* Cloud synchronization
* Multi-user support
* Doctor and caregiver dashboards
* Calendar integration

---

## 📄 License

This project is intended as a lightweight personal healthcare utility and educational Python project. Feel free to extend and customize it according to your requirements.
