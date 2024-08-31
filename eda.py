import pandas as pd

# Store Status Data
store_status_data = {
    "store_id": [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10],
    "timestamp_utc": [
        "2024-08-29 10:00:00", "2024-08-29 11:00:00", "2024-08-29 09:00:00",
        "2024-08-29 10:00:00", "2024-08-29 10:00:00", "2024-08-29 11:00:00",
        "2024-08-29 09:00:00", "2024-08-29 10:00:00", "2024-08-29 10:00:00",
        "2024-08-29 11:00:00", "2024-08-29 10:00:00", "2024-08-29 11:00:00",
        "2024-08-29 09:00:00", "2024-08-29 10:00:00", "2024-08-29 10:00:00",
        "2024-08-29 11:00:00", "2024-08-29 09:00:00", "2024-08-29 10:00:00",
        "2024-08-29 10:00:00", "2024-08-29 11:00:00"
    ],
    "status": ["active", "inactive", "active", "active", "inactive", "active", "active", "active", "active", "inactive",
               "active", "inactive", "active", "active", "inactive", "active", "inactive", "active", "active", "inactive"]
}

store_status_df = pd.DataFrame(store_status_data)
store_status_df.to_csv("store_status.csv", index=False)

# Business Hours Data
business_hours_data = {
    "store_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "dayOfWeek": [0, 1, 2, 3, 4, 5, 6, 0, 1, 2],
    "start_time_local": [
        "09:00:00", "08:00:00", "10:00:00", "11:00:00", "07:00:00",
        "09:00:00", "08:00:00", "10:00:00", "11:00:00", "07:00:00"
    ],
    "end_time_local": [
        "17:00:00", "16:00:00", "18:00:00", "19:00:00", "15:00:00",
        "17:00:00", "16:00:00", "18:00:00", "19:00:00", "15:00:00"
    ]
}

business_hours_df = pd.DataFrame(business_hours_data)
business_hours_df.to_csv("business_hours.csv", index=False)

# Store Timezone Data
store_timezone_data = {
    "store_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "timezone_str": [
        "America/New_York", "America/Los_Angeles", "America/Chicago",
        "America/New_York", "America/Chicago", "America/Los_Angeles",
        "America/New_York", "America/Chicago", "America/Los_Angeles",
        "America/New_York"
    ]
}

store_timezone_df = pd.DataFrame(store_timezone_data)
store_timezone_df.to_csv("store_timezone.csv", index=False)
