import uuid


def deterministic_uuids():
    counter = 0

    def generate():
        nonlocal counter
        counter += 1
        return uuid.UUID(bytes=(chr(counter) * 16).encode("ascii"))
    return generate
