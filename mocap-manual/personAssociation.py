import json
import os


def find_json_files(directory):
    json_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                json_files.append(os.path.join(root, file))
    return json_files


def process_file(file):
    with open(file, "r") as f:
        data = json.load(f)

    people = data["people"]
    largest_person = None
    for idx, person in enumerate(people):
        pose_keypoints_2d = person["pose_keypoints_2d"]  # x1, y1, c1, x2, y2, c2, ...

        # Compute bounding box from pose keypoints
        x = pose_keypoints_2d[0::3]
        y = pose_keypoints_2d[1::3]
        x = [x[i] for i in range(len(x)) if pose_keypoints_2d[3 * i + 2] > 0.1]
        y = [y[i] for i in range(len(y)) if pose_keypoints_2d[3 * i + 2] > 0.1]
        if len(x) == 0 or len(y) == 0:
            continue

        x_min = min(x)
        x_max = max(x)
        y_min = min(y)
        y_max = max(y)
        area = (x_max - x_min) * (y_max - y_min)

        if largest_person is None or area > largest_person["area"]:
            largest_person = {
                "area": area,
                **person,
            }

    # Keep only the largest person
    if largest_person is not None:
        largest_person.pop("area")
        largest_person["person_id"] = 0
        data["people"] = [largest_person]
    else:
        data["people"] = []

    with open(file, "w") as f:
        json.dump(data, f)


def process_all_files(directory):
    json_files = find_json_files(directory)
    for file in json_files:
        process_file(file)


if __name__ == "__main__":
    process_all_files("data/projects/orthosuper-patient8-trial7/pose")
