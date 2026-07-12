from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from connection import send_to_event_hub, generate_uber_ride_confirmation
from data import VEHICLE_TYPE_MAPPING, PAYMENT_METHOD_MAPPING

app = FastAPI()
templates = Jinja2Templates(directory="templates")

VEHICLE_TYPE_NAMES = {t['vehicle_type_id']: t['vehicle_type'] for t in VEHICLE_TYPE_MAPPING}
PAYMENT_METHOD_NAMES = {p['payment_method_id']: p['payment_method'] for p in PAYMENT_METHOD_MAPPING}


def format_timestamp(iso_string):
    return datetime.fromisoformat(iso_string).strftime("%b %d, %Y at %I:%M %p")


@app.get("/")
def booking_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/book")
def book_ride(request: Request):
    ride = generate_uber_ride_confirmation()
    result = send_to_event_hub(ride)
    return templates.TemplateResponse("confirmation.html", {
        "request": request,
        "ride": ride,
        "vehicle_type": VEHICLE_TYPE_NAMES.get(ride["vehicle_type_id"], "UberX"),
        "payment_method": PAYMENT_METHOD_NAMES.get(ride["payment_method_id"], "Card"),
        "pickup_time": format_timestamp(ride["pickup_timestamp"]),
        "dropoff_time": format_timestamp(ride["dropoff_timestamp"]),
        "sent_to_event_hub": result is not False,
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
