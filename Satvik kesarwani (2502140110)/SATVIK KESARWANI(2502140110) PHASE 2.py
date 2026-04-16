# parking_sqlite.py
# (Satvik Kesarwani) - SQLite version
import sqlite3
from datetime import datetime

DB = "parking.db"
PASSWORD = "satvik12"

FARE_MAP = {
    "1": ("Two-wheeler", 10),
    "2": ("Four-wheeler", 20),
    "3": ("Light motor vehicle (LMV)", 30)
}

def get_now_iso():
    return datetime.now().isoformat(timespec="seconds")

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS vehicles (
                    vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_plate TEXT UNIQUE NOT NULL,
                    created_at TEXT NOT NULL
                   );""")
    cur.execute("""CREATE TABLE IF NOT EXISTS parking_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    license_plate TEXT NOT NULL,
                    vehicle_type TEXT NOT NULL,
                    fare INTEGER NOT NULL,
                    check_in_time TEXT NOT NULL,
                    check_out_time TEXT,
                    status TEXT NOT NULL
                   );""")
    cur.execute("""CREATE TABLE IF NOT EXISTS modifications_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    license_plate TEXT NOT NULL,
                    old_vehicle_type TEXT,
                    new_vehicle_type TEXT,
                    old_fare INTEGER,
                    new_fare INTEGER,
                    modified_at TEXT NOT NULL
                   );""")
    conn.commit()
    conn.close()

def password_protection():
    attempts = 3
    while attempts > 0:
        password_entered = input("Enter password: ")
        if password_entered == PASSWORD:
            print("Access Granted")
            main_menu()
            return
        else:
            attempts -= 1
            if attempts > 0:
                print(f"Wrong password! {attempts} attempts left.")
            else:
                print("Access Denied. Too many incorrect attempts.")

def main_menu():
    init_db()
    while True:
        print("\n---------- PARKING LOT MANAGEMENT SYSTEM ----------")
        print("1. Check-in Vehicle (Add)")
        print("2. Check-out Vehicle (Checkout)")
        print("3. Modify Vehicle Details (active session)")
        print("4. Search for a Vehicle")
        print("5. View Reports")
        print("6. Exit")
        print("----------------------------------------------------")
        choice = input("Enter your choice (1-6): ").strip()
        if choice == "1":
            check_in()
        elif choice == "2":
            check_out()
        elif choice == "3":
            modify_vehicle()
        elif choice == "4":
            search_vehicle()
        elif choice == "5":
            view_reports()
        elif choice == "6":
            print("\nThanks for visiting. Goodbye!\n")
            break
        else:
            print("\nInvalid choice! Please select an option from 1 to 6.")

def check_in():
    license_plate = input("Enter license plate number: ").strip().upper()
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    # Check if vehicle already IN
    cur.execute("SELECT * FROM parking_sessions WHERE license_plate=? AND status='IN';", (license_plate,))
    if cur.fetchone():
        print(f"Vehicle with license plate {license_plate} is already checked in.")
        conn.close()
        return

    print("Vehicle type:\n1- Two-wheelers\n2- Four-wheelers\n3- Light motor vehicles (LMVs)")
    choice = input("Enter your choice (1-3): ").strip()
    if choice not in FARE_MAP:
        print("Invalid choice! try again.")
        conn.close()
        return
    vehicle_type, fare = FARE_MAP[choice]

    now = get_now_iso()

    # Optional: add to vehicles master if not exists
    try:
        cur.execute("INSERT OR IGNORE INTO vehicles (license_plate, created_at) VALUES (?,?);", (license_plate, now))
    except Exception:
        pass

    # Insert session
    cur.execute("""INSERT INTO parking_sessions
                   (license_plate, vehicle_type, fare, check_in_time, status)
                   VALUES (?,?,?,?, 'IN');""", (license_plate, vehicle_type, fare, now))
    conn.commit()
    conn.close()
    print(f"Vehicle {license_plate} checked in successfully! Fare = Rs. {fare} (check-in at {now})")

def check_out():
    license_plate = input("Enter license plate to check out: ").strip().upper()
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT session_id, fare, check_in_time FROM parking_sessions WHERE license_plate=? AND status='IN' ORDER BY check_in_time DESC LIMIT 1;", (license_plate,))
    row = cur.fetchone()
    if not row:
        print("Vehicle not found or already checked out. Please check the entered plate number.")
        conn.close()
        return

    session_id, fare, check_in_time = row
    now = get_now_iso()
    # Update session
    cur.execute("UPDATE parking_sessions SET check_out_time=?, status='OUT' WHERE session_id=?;", (now, session_id))
    conn.commit()
    conn.close()
    print(f"License plate {license_plate} checked out successfully.")
    print(f"Checked in at: {check_in_time}  |  Checked out at: {now}  |  Fare: Rs. {fare}")

def modify_vehicle():
    """
    Modify the active session's vehicle type/fare. This logs the modification.
    """
    license_plate = input("Enter license plate number to modify (active session): ").strip().upper()
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT session_id, vehicle_type, fare FROM parking_sessions WHERE license_plate=? AND status='IN' ORDER BY check_in_time DESC LIMIT 1;", (license_plate,))
    row = cur.fetchone()
    if not row:
        print("Active vehicle session not found for that plate.")
        conn.close()
        return

    session_id, old_vehicle_type, old_fare = row
    print("Vehicle type:\n1- Two-wheelers\n2- Four-wheelers\n3- Light motor vehicles (LMVs)")
    type_choice = input("Enter type code (1-3): ").strip()
    if type_choice not in FARE_MAP:
        print("Invalid selection. Choose again.")
        conn.close()
        return
    new_vehicle_type, new_fare = FARE_MAP[type_choice]

    # Update session
    cur.execute("""UPDATE parking_sessions
                   SET vehicle_type=?, fare=?
                   WHERE session_id=?;""", (new_vehicle_type, new_fare, session_id))

    # Log modification
    modified_at = get_now_iso()
    cur.execute("""INSERT INTO modifications_log
                   (session_id, license_plate, old_vehicle_type, new_vehicle_type, old_fare, new_fare, modified_at)
                   VALUES (?,?,?,?,?,?,?);""", (session_id, license_plate, old_vehicle_type, new_vehicle_type, old_fare, new_fare, modified_at))
    conn.commit()
    conn.close()
    print("Vehicle record updated and modification logged.")

def search_vehicle():
    license_plate = input("Enter license plate number to search: ").strip().upper()
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # Find latest session (in or out)
    cur.execute("SELECT * FROM parking_sessions WHERE license_plate=? ORDER BY check_in_time DESC LIMIT 1;", (license_plate,))
    row = cur.fetchone()
    if not row:
        print("Vehicle not found.")
        conn.close()
        return

    # row indices: session_id, license_plate, vehicle_type, fare, check_in_time, check_out_time, status
    session_id, lp, vtype, fare, cin, cout, status = row
    print("------ Vehicle Found ------")
    print(f"License Plate: {lp}")
    print(f"Vehicle Type: {vtype}")
    print(f"Fare: Rs. {fare}")
    print(f"Check-in: {cin}")
    print(f"Check-out: {cout if cout else 'Still parked'}")
    print(f"Status: {status}")
    conn.close()

def view_reports():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    # 1) Current parked vehicles
    print("\n--- Currently Parked Vehicles ---")
    cur.execute("SELECT license_plate, vehicle_type, fare, check_in_time FROM parking_sessions WHERE status='IN' ORDER BY check_in_time;")
    rows = cur.fetchall()
    if not rows:
        print("No vehicles currently parked.")
    else:
        two= four = lmv = 0
        total_active_fare = 0
        for lp, vtype, fare, cin in rows:
            print(f"{lp}: {vtype}, Rs. {fare}, check-in: {cin}")
            if vtype == "Two-wheeler":
                two += 1
            elif vtype == "Four-wheeler":
                four += 1
            elif "LMV" in vtype:
                lmv += 1
            total_active_fare += fare
        print("\n--- Active Summary ---")
        print(f"Two-wheelers: {two}")
        print(f"Four-wheelers: {four}")
        print(f"Light motor vehicles (LMV): {lmv}")
        print(f"Total vehicles (parked): {len(rows)}")
        print(f"Potential revenue if all checked out now (sum of fares): Rs. {total_active_fare}")

    # 2) Revenue summary (completed sessions)
    print("\n--- Revenue (Completed Sessions) ---")
    cur.execute("SELECT COUNT(*), IFNULL(SUM(fare),0) FROM parking_sessions WHERE status='OUT';")
    cnt, revenue = cur.fetchone()
    print(f"Total completed sessions: {cnt}")
    print(f"Total revenue collected: Rs. {revenue}")

    # 3) Revenue for a date range (optional quick prompt)
    choice = input("\nDo you want revenue for a date range? (y/n): ").strip().lower()
    if choice == 'y':
        start = input("Start date (YYYY-MM-DD) or press Enter for no lower bound: ").strip()
        end = input("End date (YYYY-MM-DD) or press Enter for no upper bound: ").strip()
        # Build query
        q = "SELECT COUNT(*), IFNULL(SUM(fare),0) FROM parking_sessions WHERE status='OUT'"
        params = []
        if start:
            q += " AND date(check_out_time) >= date(?)"
            params.append(start)
        if end:
            q += " AND date(check_out_time) <= date(?)"
            params.append(end)
        cur.execute(q, tuple(params))
        cnt_range, revenue_range = cur.fetchone()
        print(f"Completed sessions in range: {cnt_range}")
        print(f"Revenue in range: Rs. {revenue_range}")

    conn.close()

if __name__ == "__main__":
    password_protection()
