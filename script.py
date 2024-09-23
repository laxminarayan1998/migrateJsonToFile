import json
from datetime import datetime
import random
import string

try:
    from bson import ObjectId
    from bson.json_util import dumps, loads, RELAXED_JSON_OPTIONS
except ImportError:
    print("Error: bson module not found. Please install pymongo by running: pip install pymongo")
    exit(1)

def generate_random_id():
    return ObjectId()

def migrate_bookings(old_bookings):
    new_bookings = []
    booking_id_counter = 1

    for old_booking in old_bookings:
        name_parts = old_booking["name"].split()
        first_name = name_parts[0]
        last_name = name_parts[-1] if len(name_parts) > 1 else "NA"

        phone_number = ''.join(filter(str.isdigit, old_booking["phone"]))
        phone_number = f"91{phone_number[-10:]}"

        new_booking = {
            "_id": ObjectId(old_booking["_id"]["$oid"]),
            "bookingId": f"WEDIUM{str(booking_id_counter).zfill(3)}",
            "otp": old_booking["otp"],
            "uid": str(generate_random_id()),
            "firstName": first_name,
            "lastName": last_name,
            "bookingTime": old_booking["bookingTime"],
            "bookingDate": datetime.strptime(old_booking["orderDate"], "%m/%d/%Y"),
            "products": [
                {
                    "productId": ObjectId(old_booking["ServiceData"]["_id"]["$oid"]),
                    "name": old_booking["ServiceData"]["name"],
                    "price": old_booking["ServiceData"]["price"],
                    "quantity": 1,
                    "discount": 0,
                    "discountPercentage": 0,
                    "_id": generate_random_id()
                }
            ],
            "address": {
                "firstName": first_name,
                "lastName": last_name,
                "street": old_booking["address"],
                "city": old_booking["cityData"]["city"],
                "state": old_booking["cityData"]["state"],
                "district": "NA",
                "postalCode": "0",
                "country": "IN",
                "phoneNumber": phone_number,
                "optionalPhoneNumber": phone_number
            },
            "status": old_booking["orderStatus"],
            "bookingAmount": {
                "totalProductPrice": old_booking["ServiceData"]["price"],
                "couponDiscount": 0,
                "finalAmount": old_booking["ServiceData"]["price"],
                "originalTotalPrice": old_booking["ServiceData"]["price"]
            },
            "otpGeneratedAt": datetime.fromisoformat(old_booking["createdAt"]["$date"].rstrip('Z')),
            "createdAt": datetime.fromisoformat(old_booking["createdAt"]["$date"].rstrip('Z')),
            "updatedAt": datetime.fromisoformat(old_booking["updatedAt"]["$date"].rstrip('Z')),
            "__v": 0,
            "vendor": {
                "vendorId": ObjectId(old_booking["vendorData"]["_id"]["$oid"]),
                "fullName": old_booking["vendorData"]["name"],
                "phoneNumber": f"91{''.join(filter(str.isdigit, old_booking['vendorData']['phone']))[-10:]}"
            }
        }

        new_bookings.append(new_booking)
        booking_id_counter += 1

    return new_bookings

# Load the JSON data
input_file_path = 'test.orders.json'
output_file_path = 'products.json'

with open(input_file_path, 'r') as file:
    old_bookings = json.load(file)

# Migrate the bookings
migrated_bookings = migrate_bookings(old_bookings)

# Save the migrated data to a new JSON file using bson.json_util
with open(output_file_path, 'w') as file:
    file.write(dumps(migrated_bookings, indent=2, json_options=RELAXED_JSON_OPTIONS))

print(f"Migration completed. Migrated data saved to {output_file_path}")