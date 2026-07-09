from fastapi import FastAPI, HTTPException, Query
import requests
import uvicorn
import threading
import time

app = FastAPI(title="Local Open-Meteo Gateway Simulator")

provider_state = {
    "status": "up"
}


def auto_restart_after(seconds: int):
    print(f"[OPEN-METEO-GATEWAY] Provider is DOWN for {seconds} seconds")
    time.sleep(seconds)

    print("[OPEN-METEO-GATEWAY] Restarting provider...")
    time.sleep(2)

    provider_state["status"] = "up"
    print("[OPEN-METEO-GATEWAY] Provider restarted successfully")
    print("[OPEN-METEO-GATEWAY] Provider status: UP")


@app.get("/")
def root():
    return {
        "service": "Local Open-Meteo Gateway Simulator",
        "status": provider_state["status"]
    }


@app.get("/status")
def status():
    return {
        "status": provider_state["status"]
    }


@app.post("/control/unreachable")
def make_unreachable(seconds: int = 30):
    provider_state["status"] = "down"

    print("===================================================")
    print("[OPEN-METEO-GATEWAY] Provider status changed to DOWN")
    print("[OPEN-METEO-GATEWAY] Simulating live provider unreachable")
    print("===================================================")

    thread = threading.Thread(
        target=auto_restart_after,
        args=(seconds,),
        daemon=True
    )
    thread.start()

    return {
        "status": "down",
        "message": f"Provider unreachable for {seconds} seconds, then auto restart"
    }


@app.post("/control/available")
def make_available():
    provider_state["status"] = "up"

    print("===================================================")
    print("[OPEN-METEO-GATEWAY] Provider manually changed to UP")
    print("===================================================")

    return {
        "status": "up",
        "message": "Provider is available"
    }


@app.get("/v1/search")
def geocoding_proxy(
    name: str = Query(...),
    count: int = 1,
    language: str = "en",
    format: str = "json"
):
    if provider_state["status"] == "down":
        print("[OPEN-METEO-GATEWAY] DOWN: geocoding request blocked")
        raise HTTPException(
            status_code=503,
            detail="Open-Meteo provider is unreachable"
        )

    print(f"[OPEN-METEO-GATEWAY] UP: forwarding geocoding request for city={name}")

    response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={
            "name": name,
            "count": count,
            "language": language,
            "format": format
        },
        timeout=10
    )

    response.raise_for_status()
    return response.json()


@app.get("/v1/forecast")
def forecast_proxy(
    latitude: float,
    longitude: float,
    current: str
):
    if provider_state["status"] == "down":
        print("[OPEN-METEO-GATEWAY] DOWN: forecast request blocked")
        raise HTTPException(
            status_code=503,
            detail="Open-Meteo provider is unreachable"
        )

    print(
        "[OPEN-METEO-GATEWAY] UP: forwarding forecast request "
        f"latitude={latitude}, longitude={longitude}"
    )

    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": current
        },
        timeout=10
    )

    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    print("===================================================")
    print("[OPEN-METEO-GATEWAY] Starting Local Open-Meteo Gateway")
    print("[OPEN-METEO-GATEWAY] URL: http://127.0.0.1:9001")
    print("[OPEN-METEO-GATEWAY] Initial provider status: UP")
    print("===================================================")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=9001
    )
