from pathlib import Path
import requests
import canvas as c
import json
import os

def sortByAttr(data, attribute):
    # Use sorted with the attribute as the key
    descending = attribute.startswith("-")
    attribute = attribute[1:] if descending else attribute

    try:
        return attribute, sorted(
            data,
            key=lambda item: normalizeValue(item[attribute]) if isinstance(item, dict) else float("inf"),
            reverse=descending
        )
    except KeyError:
        print(f"Invalid attribute: {attribute}")
        return attribute, sorted(
            data,
            key=lambda item: normalizeValue(item["first"]) if isinstance(item, dict) else float("inf"),
            reverse=descending
        )
        # return data

def normalizeValue(value):
    """Convert values to a common type for comparison."""
    if isinstance(value, (int, float)):
        return value
    elif isinstance(value, str):
        try:
            # Attempt to convert to a number if possible
            num_value = float(value)
            return num_value if "." in value else int(num_value)
        except ValueError:
            # If not a number, return lowercase string for consistent sorting
            return value.lower()
    return value  # Return as-is for other types

def sendMessage(courseId, studentId, subject, body):
    payload = {
        "recipients": studentId,
        "subject": f"WDD 330 - {subject}",
        "body": f"{body}",
        "context_code": f"course_{courseId}",
        "bulk_message": True
    }
    response = requests.post(f"{c.canvasURL}/conversations?force_new=true", headers=c.headers, json=payload )
    status = response.json()
    return status

def getCanvasData(url, params, fileName, folder):
    cacheDir = Path(f"./cache/{folder}")
    cacheDir.mkdir(parents=True, exist_ok=True)

    cacheFile = cacheDir / f"{fileName}.json"

    # return cached data if it exists
    if cacheFile.exists():
        return readJSON(fileName, folder)

    # otherwise fetch from Canvas
    response = requests.get( f"{c.canvasURL}{url}", headers=c.headers, params=params)
    response.raise_for_status()

    data = response.json()

    # cache the result
    writeJSON(fileName, data, folder)

    return data

def writeJSON(fileName, data, folder):
    # Write JSON data to file
    with open(f"./cache/{folder}/{fileName}.json", "w") as file:
        json.dump(data, file, indent=4)
        # print(f"Done writing {fileName}")


def readJSON(fileName, folder):
    # Read JSON data from file and convert it back to a dictionary
    path = f"./cache/{folder}/{fileName}.json"

    with open(path, "r") as file:
        data = json.load(file)
        # print(f"Done reading {fileName}")
        return data

def checkFolders():
    # Check if the cache directory exists, if not, create it
    if not os.path.exists("./cache"):
        os.makedirs("./cache")
