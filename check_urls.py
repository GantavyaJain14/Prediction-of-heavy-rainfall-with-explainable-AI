import requests

candidates = [
    "https://mausam.imd.gov.in/Satellite/3D_Globe_IR1.jpg",
    "https://satellite.imd.gov.in/img/3Dimg/3D-IR1.jpg",
    "https://mausam.imd.gov.in/Satellite/IMD_Global_IR1.jpg",
    "https://mausam.imd.gov.in/Satellite/img/3D_IR1.jpg"
]

print("Checking URLs...")
for url in candidates:
    try:
        r = requests.head(url, timeout=5)
        print(f"[{r.status_code}] {url}")
    except Exception as e:
        print(f"[Error] {url}: {e}")
