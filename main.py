from config import image_path, crop_coordinates
from image_processing import preprocess_image
from ocr_api import send_to_ocr_api
from postprocessing import extract_numbers, extract_on_off
from mqtt_publisher import send_mqtt_message
import json

all_results = []
on_off_results = []

for i, coords in enumerate(crop_coordinates):
    region_id = i + 1
    processed_path = f"/home/CITSEM/Ocr_Project/OCR_MQTT/Orignal_Image/processed_region_{region_id}.jpeg"

    if preprocess_image(image_path, coords, processed_path):
        response = send_to_ocr_api(processed_path)
        if response.status_code == 200:
            result = response.json()
            if not result.get("IsErroredOnProcessing"):
                text = result["ParsedResults"][0]["ParsedText"]
                print(f"[DEBUG] Region {region_id} OCR Text:\n{text}")
                if region_id <= 2:
                    all_results.extend(extract_numbers(text, region_id))
                else:
                    on_off_results.extend(extract_on_off(text, region_id))
            else:
                print(f"[ERROR] Region {region_id} OCR Error: {result.get('ErrorMessage')}")
        else:
            print(f"[ERROR] Region {region_id} API HTTP Error: {response.status_code}")

message = {
    "status": "success",
    "Module_Numbers": all_results,
    "Module_ON_Lines": on_off_results
}

send_mqtt_message(message)
print("[INFO] Final Message:", json.dumps(message, indent=2))


