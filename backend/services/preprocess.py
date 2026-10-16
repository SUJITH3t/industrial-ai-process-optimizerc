import pandas as pd


def preprocess_input(data):
    """
    Convert JSON input into a DataFrame.
    """

    df = pd.DataFrame([{
        "temperature": float(data.get("temperature", 0)),
        "pressure": float(data.get("pressure", 0)),
        "humidity": float(data.get("humidity", 0)),
        "speed": float(data.get("speed", 0)),
        "vibration": float(data.get("vibration", 0)),
        "material": float(data.get("material", 0)),
        "power": float(data.get("power", 0))
    }])

    return df


def validate_input(data):
    """
    Validate required fields.
    """

    required_fields = [
        "temperature",
        "pressure",
        "humidity",
        "speed",
        "vibration",
        "material",
        "power"
    ]

    for field in required_fields:

        if field not in data:
            return False, f"Missing field: {field}"

        if data[field] == "":
            return False, f"{field} cannot be empty"

    return True, "Valid Input"