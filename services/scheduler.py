import os
import sys
import threading
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from Config.settings import CHECK_INTERVAL_SECONDS
from services.data_services import load_medicines

class Scheduler:
    def __init__(self):
        self.medicines = load_medicines()
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self.run_scheduler).start()

    def stop(self):
        self.running = False

    def run_scheduler(self):
        while self.running:
            now = datetime.now().time()
            for medicine in self.medicines:
                if medicine['time'] == now.strftime("%H:%M"):
                    print(f"Time to take {medicine['name']}!")
            threading.Event().wait(CHECK_INTERVAL_SECONDS)
