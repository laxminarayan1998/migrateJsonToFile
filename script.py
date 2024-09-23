import json
from datetime import datetime

try:
    from bson import ObjectId
    from bson.json_util import dumps, RELAXED_JSON_OPTIONS
except ImportError:
    print("Error: bson module not found. Please install pymongo by running: pip install pymongo")
    exit(1)

# Function to migrate bookings
def migrate_bookings(old_bookings):
    new_bookings = []
    profiles = {}
    booking_id_counter = 1

    for old_booking in old_bookings:
        name_parts = old_booking["name"].split()
        first_name = name_parts[0]
        last_name = name_parts[-1] if len(name_parts) > 1 else "NA"

        phone_number = ''.join(filter(str.isdigit, old_booking["phone"]))
        
        # Check if the number length is 10 and prepend 91 if necessary
        if len(phone_number) == 10:
            phone_number_with_code = f"91{phone_number}"
        else:
            phone_number_with_code = phone_number  # Use the existing number

        # Create profile if it doesn't exist
        if phone_number_with_code not in profiles:
            uid = ObjectId()  # Use ObjectId as uid
            profiles[phone_number_with_code] = {
                "_id": uid,
                "uid": str(uid),  # Convert ObjectId to string for consistency
                "fullName": first_name + " " + last_name,
                "email": old_booking.get("email", ""),
                "phoneNumber": int(phone_number_with_code),  # Store as an integer
                "profileImage": old_booking.get("profileImage", ""),
                "coverImage": old_booking.get("coverImage", ""),
                "fcmToken": old_booking.get("fcmToken", ""),
                "status": "active",
                "updatedAt": datetime.utcnow()
            }

        new_booking = {
            "_id": ObjectId(),  # Use uid from the profile
            "bookingId": f"WEDIUM{str(booking_id_counter).zfill(3)}",
            "otp": old_booking["otp"],
            "uid": profiles[phone_number_with_code]["uid"],  # Use the uid from the profile
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
                    "_id": ObjectId()
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
                "phoneNumber": phone_number_with_code,  # Store formatted phone number
                "optionalPhoneNumber": phone_number_with_code
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

    return new_bookings, list(profiles.values())

# Load the JSON data
input_file_path = 'test.orders.json'
output_file_path = 'products.json'
profiles_output_path = 'profiles.json'

with open(input_file_path, 'r') as file:
    old_bookings = json.load(file)

# Migrate the bookings and create profiles
migrated_bookings, new_profiles = migrate_bookings(old_bookings)

# Save the migrated data to a new JSON file for bookings
with open(output_file_path, 'w') as file:
    file.write(dumps(migrated_bookings, indent=2, json_options=RELAXED_JSON_OPTIONS))

# Save the newly created profiles to a new JSON file
with open(profiles_output_path, 'w') as file:
    file.write(dumps(new_profiles, indent=2, json_options=RELAXED_JSON_OPTIONS))

print(f"Migration completed. Migrated data saved to {output_file_path} and profiles saved to {profiles_output_path}")
