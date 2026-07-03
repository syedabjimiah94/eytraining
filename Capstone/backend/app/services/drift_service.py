class DriftService:
    REQUIRED_WEATHER_FIELDS = [
        "city",
        "temperature",
        "humidity",
        "wind_speed",
        "condition",
        "source",
    ]

    def detect_schema_drift(self, data: dict):
        missing_fields = [
            field for field in self.REQUIRED_WEATHER_FIELDS
            if field not in data
        ]

        if missing_fields:
            return {
                "drift_detected": True,
                "drift_type": "API_SCHEMA_DRIFT",
                "message": f"Missing fields: {missing_fields}",
                "severity": "MEDIUM",
            }

        return {
            "drift_detected": False,
            "drift_type": "NONE",
            "message": "No API schema drift detected",
            "severity": "LOW",
        }

    def detect_data_anomaly(self, data: dict):
        temperature = data.get("temperature")
        humidity = data.get("humidity")
        wind_speed = data.get("wind_speed")

        anomalies = []

        if isinstance(temperature, (int, float)) and (temperature < -20 or temperature > 60):
            anomalies.append("Temperature out of expected range")

        if isinstance(humidity, (int, float)) and (humidity < 0 or humidity > 100):
            anomalies.append("Humidity out of expected range")

        if isinstance(wind_speed, (int, float)) and (wind_speed < 0 or wind_speed > 150):
            anomalies.append("Wind speed out of expected range")

        if anomalies:
            return {
                "drift_detected": True,
                "drift_type": "DATA_ANOMALY_DRIFT",
                "message": ", ".join(anomalies),
                "severity": "MEDIUM",
            }

        return {
            "drift_detected": False,
            "drift_type": "NONE",
            "message": "No data anomaly drift detected",
            "severity": "LOW",
        }

    def analyze(self, data: dict):
        schema_result = self.detect_schema_drift(data)

        if schema_result["drift_detected"]:
            return schema_result

        return self.detect_data_anomaly(data)