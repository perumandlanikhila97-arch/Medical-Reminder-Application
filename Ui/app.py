import csv
import os
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from Config.settings import CHECK_INTERVAL_SECONDS
from services.data_services import load_medicines, save_medicines
from services.prescription_parser import parse_prescription_file
from services.log_service import ensure_log, log_event
from utils.validators import parse_times_field


class MedicineApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Medicine Reminder")
        self.master.geometry("840x560")
        self.master.resizable(False, False)

        self.medicines = load_medicines()
        self.editing_index = None
        self.scheduler_running = False
        self._notification_date = None
        self._notified_items = set()

        self.build_ui()
        self.refresh_treeview()

    def build_ui(self):
        top_frame = tk.Frame(self.master)
        top_frame.pack(fill="x", padx=10, pady=10)

        upload_button = tk.Button(top_frame, text="Upload Prescription", command=self.upload_prescription, width=18)
        upload_button.pack(side="left", padx=4)

        show_log_button = tk.Button(top_frame, text="Show Log", command=self.show_log, width=12)
        show_log_button.pack(side="left", padx=4)

        self.scheduler_button = tk.Button(top_frame, text="Start Scheduler", command=self.start_scheduler, width=14)
        self.scheduler_button.pack(side="left", padx=4)

        input_frame = tk.LabelFrame(self.master, text="Add or edit medicine")
        input_frame.pack(fill="x", padx=10, pady=(0, 10))

        tk.Label(input_frame, text="Name").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        self.name_entry = tk.Entry(input_frame, width=22)
        self.name_entry.grid(row=0, column=1, padx=6, pady=6)

        tk.Label(input_frame, text="Dose").grid(row=0, column=2, sticky="w", padx=6, pady=6)
        self.dose_entry = tk.Entry(input_frame, width=16)
        self.dose_entry.grid(row=0, column=3, padx=6, pady=6)

        tk.Label(input_frame, text="Times (HH:MM sep ; or ,)").grid(row=0, column=4, sticky="w", padx=6, pady=6)
        self.times_entry = tk.Entry(input_frame, width=26)
        self.times_entry.grid(row=0, column=5, padx=6, pady=6)

        tk.Label(input_frame, text="Notes").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.notes_entry = tk.Entry(input_frame, width=76)
        self.notes_entry.grid(row=1, column=1, columnspan=5, padx=6, pady=6, sticky="w")

        self.add_button = tk.Button(input_frame, text="Add", command=self.add_medicine, width=12)
        self.add_button.grid(row=2, column=5, sticky="e", padx=6, pady=8)

        table_frame = tk.Frame(self.master)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        columns = ("name", "dose", "times", "notes")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("name", text="Name")
        self.tree.heading("dose", text="Dose")
        self.tree.heading("times", text="Times")
        self.tree.heading("notes", text="Notes")
        self.tree.column("name", width=180, anchor="w")
        self.tree.column("dose", width=120, anchor="center")
        self.tree.column("times", width=220, anchor="center")
        self.tree.column("notes", width=280, anchor="w")
        self.tree.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(fill="y", side="right")

        bottom_frame = tk.Frame(self.master)
        bottom_frame.pack(fill="x", padx=10, pady=(0, 10))

        edit_button = tk.Button(bottom_frame, text="Edit Selected", command=self.edit_selected, width=16)
        edit_button.pack(side="left", padx=4)

        delete_button = tk.Button(bottom_frame, text="Delete Selected", command=self.delete_selected, width=16)
        delete_button.pack(side="left", padx=4)

        export_button = tk.Button(bottom_frame, text="Export Schedule CSV", command=self.export_schedule_csv, width=18)
        export_button.pack(side="right", padx=4)

    def upload_prescription(self):
        file_path = filedialog.askopenfilename(
            title="Upload Prescription",
            filetypes=[("Prescription files", "*.csv *.txt"), ("All files", "*.*")],
        )

        if not file_path:
            return

        try:
            new_medicines = parse_prescription_file(file_path)
        except Exception as exc:
            messagebox.showerror("Upload Error", f"Unable to import prescription:\n{exc}")
            return

        if not new_medicines:
            messagebox.showwarning("No Medicines", "The selected prescription did not contain valid medicine entries.")
            return

        self.medicines.extend(new_medicines)
        save_medicines(self.medicines)
        self.refresh_treeview()
        messagebox.showinfo("Upload Complete", f"Imported {len(new_medicines)} medicine record(s).")

    def add_medicine(self):
        name = self.name_entry.get().strip()
        dose = self.dose_entry.get().strip()
        times_raw = self.times_entry.get().strip()
        notes = self.notes_entry.get().strip()

        if not name:
            messagebox.showwarning("Missing Name", "Please enter a medicine name.")
            return

        times = parse_times_field(times_raw)
        if not times:
            messagebox.showwarning("Invalid Times", "Please enter one or more valid HH:MM times separated by commas or semicolons.")
            return

        medicine = {
            "name": name,
            "dose": dose,
            "times": times,
            "notes": notes,
        }

        if self.editing_index is not None:
            self.medicines[self.editing_index] = medicine
            self.editing_index = None
            self.add_button.config(text="Add")
        else:
            self.medicines.append(medicine)

        save_medicines(self.medicines)
        self.refresh_treeview()
        self.clear_form()

    def edit_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Item", "Please select a medicine to edit.")
            return

        selected_index = self.tree.index(selected[0])
        medicine = self.medicines[selected_index]

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, medicine.get("name", ""))
        self.dose_entry.delete(0, tk.END)
        self.dose_entry.insert(0, medicine.get("dose", ""))
        self.times_entry.delete(0, tk.END)
        self.times_entry.insert(0, "; ".join(medicine.get("times", [])))
        self.notes_entry.delete(0, tk.END)
        self.notes_entry.insert(0, medicine.get("notes", ""))

        self.editing_index = selected_index
        self.add_button.config(text="Save")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Select Item", "Please select a medicine to delete.")
            return

        selected_index = self.tree.index(selected[0])
        medicine = self.medicines[selected_index]
        confirm = messagebox.askyesno(
            "Delete Medicine",
            f"Delete '{medicine.get('name', '')}' from the schedule?",
        )
        if not confirm:
            return

        self.medicines.pop(selected_index)
        save_medicines(self.medicines)
        self.refresh_treeview()
        self.clear_form()

    def refresh_treeview(self):
        self.tree.delete(*self.tree.get_children())
        for medicine in self.medicines:
            times_text = ", ".join(medicine.get("times", []))
            self.tree.insert(
                "",
                "end",
                values=(
                    medicine.get("name", ""),
                    medicine.get("dose", ""),
                    times_text,
                    medicine.get("notes", ""),
                ),
            )

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.dose_entry.delete(0, tk.END)
        self.times_entry.delete(0, tk.END)
        self.notes_entry.delete(0, tk.END)
        self.editing_index = None
        self.add_button.config(text="Add")

    def show_log(self):
        ensure_log()
        log_window = tk.Toplevel(self.master)
        log_window.title("Medicine Log")
        log_window.geometry("760x420")

        text_widget = tk.Text(log_window, wrap="none", state="normal")
        text_widget.pack(fill="both", expand=True)

        with open(os.path.join(os.getcwd(), "data", "medicine_log.csv"), "r", encoding="utf-8") as f:
            content = f.read()
            text_widget.insert("1.0", content)

        text_widget.config(state="disabled")

    def export_schedule_csv(self):
        if not self.medicines:
            messagebox.showinfo("No Schedule", "There are no medicine schedules to export.")
            return

        save_path = filedialog.asksaveasfilename(
            title="Export Schedule CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )
        if not save_path:
            return

        with open(save_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "dose", "times", "notes"])
            for medicine in self.medicines:
                writer.writerow([
                    medicine.get("name", ""),
                    medicine.get("dose", ""),
                    "; ".join(medicine.get("times", [])),
                    medicine.get("notes", ""),
                ])

        messagebox.showinfo("Export Complete", f"Schedule exported to {save_path}")

    def start_scheduler(self):
        if self.scheduler_running:
            messagebox.showinfo("Scheduler Running", "The scheduler is already running.")
            return

        self.scheduler_running = True
        self.scheduler_button.config(text="Scheduler Running", state="disabled")
        thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        thread.start()
        messagebox.showinfo("Scheduler Started", "Background scheduler started successfully.")

    def _scheduler_loop(self):
        while self.scheduler_running:
            now = datetime.now()
            current_date = now.date()
            if self._notification_date != current_date:
                self._notification_date = current_date
                self._notified_items.clear()

            current_time = now.strftime("%H:%M")
            medicines = load_medicines()
            for medicine in medicines:
                for scheduled_time in medicine.get("times", []):
                    notify_id = f"{medicine.get('name')}|{scheduled_time}|{current_date}"
                    if scheduled_time == current_time and notify_id not in self._notified_items:
                        self._notified_items.add(notify_id)
                        self.master.after(0, lambda m=medicine, t=scheduled_time: self._notify_medication(m, t))

            time.sleep(CHECK_INTERVAL_SECONDS)

    def _notify_medication(self, medicine, scheduled_time):
        title = "Medication Reminder"
        message = f"Time to take {medicine.get('name')} ({medicine.get('dose', '')}) at {scheduled_time}."
        messagebox.showinfo(title, message)
        log_event(
            medicine.get("name", ""),
            medicine.get("dose", ""),
            f"Scheduled time {scheduled_time}",
            "reminder",
        )
