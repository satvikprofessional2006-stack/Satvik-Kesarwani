#Parking Lot Fee System
# (Satvik Kesarwani)(2502140110)
from datetime import datetime
vehicles = []


def password_protection():
    password = "satvik12"
    attempts = 3
    while attempts > 0:
        password_entered = input("Enter password: ")
        if password_entered == password:
            print("Access Granted")
            main_menu()
            break
        else:
            attempts -= 1
            if attempts > 0:
                print(f"Wrong password! {attempts} attempts left.")
            else:
                print("Access Denied. Too many incorrect attempts.")

def main_menu():
    while True:
        print("\n---------- PARKING LOT MANAGEMENT SYSTEM ----------")
        print("1. Check-in Vehicle (Add)")
        print("2. Check-out Vehicle (Delete)")
        print("3. Modify Vehicle Details")
        print("4. Search for a Vehicle")
        print("5. View Reports")
        print("6. Exit")
        print("----------------------------------------------------")

        choice = input("Enter your choice (1-6): ")

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
            return(password_protection())
        else:
            print("\nInvalid choice! Please select an option from 1 to 6.")

def check_in():
    number = input("Enter license plate number: ")
    for v in vehicles:
        if v['license_plate']==number:
            print(f"vehicle of license plate {number} already checked in.")
            return
    print("Vehicle type:\n1- Two-wheelers\n2- Four-wheelers\n3- Light motor vehicles (LMVs)")
    choice = input("Enter your choice (1-3): ")

    if choice == "1":
        vehicle_type = "Two-wheeler"
        fare = 10
    elif choice == "2":
        vehicle_type = "Four-wheeler"
        fare = 20
    elif choice == "3":
        vehicle_type = "Light motor vehicle (LMV)"
        fare = 30
    else:
        print("Invalid choice! try again.")
        return


    v = {
        "license_plate": number,
        "vehicle_type": vehicle_type,
        "fare": fare,
        "check_in_time": datetime.now()
    }


    vehicles.append(v)
    print(f"Vehicle {number} checked in successfully! Fare = Rs. {fare}")

def check_out():
    number = input("Enter license plate to check out: ")
    for v in vehicles:
        if v["license_plate"] == number:
            check_out_time = datetime.now()
            vehicles.remove(v)
            print(f"License plate {number} checked out successfully.")
            return
    print("Vehicle not found. Please check the entered plate number.")

def modify_vehicle():
    print("-----Modify Vehicle Details-----")
    plate = input("Enter license plate number to modify: ")
    for v in vehicles:
        if v["license_plate"] == plate:
            print("Vehicle type:\n1- Two-wheelers\n2- Four-wheelers\n3- Light motor vehicles (LMVs)")
            type_choice = input("Enter type code (1-3): ")
            if type_choice == "1":
                v["vehicle_type"] = "Two-wheeler"
                v["fare"] = 10
            elif type_choice == "2":
                v["vehicle_type"] = "Four-wheeler"
                v["fare"] = 20
            elif type_choice == "3":
                v["vehicle_type"] = "Light motor vehicle (LMV)"
                v["fare"] = 30
            else:
                print("Invalid selection. Choose again.")
                return
            print("Vehicle record updated.")
            return
    print("Vehicle not found.")

def search_vehicle():
    plate = input("Enter license plate number to search: ")
    for v in vehicles:
        if v["license_plate"] == plate:
            print("------ Vehicle Found ------")
            print(f"License Plate: {v['license_plate']}")
            print(f"Vehicle Type: {v['vehicle_type']}")
            print(f"Fare: Rs. {v['fare']}")
            return
    print("Vehicle not found.")

def view_reports():
    print("\n--- Parked Vehicles Records ---")
    two_count = 0
    four_count = 0
    lmv_count = 0
    total_fare = 0

    for v in vehicles:
        print(f"{v['license_plate']}: {v['vehicle_type']}, Rs. {v['fare']},check in time:{v['check_in_time']}")
        if v['vehicle_type'] == "Two-wheeler":
            two_count += 1
        elif v['vehicle_type'] == "Four-wheeler":
            four_count += 1
        elif v['vehicle_type'] == "Light motor vehicle (LMV)":
            lmv_count += 1
        total_fare += v['fare']

    if len(vehicles) == 0:
        print("No records found.")
    else:
        print("\n--- Summary ---")
        print(f"Two-wheelers: {two_count}")
        print(f"Four-wheelers: {four_count}")
        print(f"Light motor vehicles (LMV): {lmv_count}")
        print(f"Total vehicles: {len(vehicles)}")
        print(f"Total revenue: Rs. {total_fare}")

#main
password_protection()
