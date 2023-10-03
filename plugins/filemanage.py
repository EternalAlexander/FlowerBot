import pickle


def syncto(name, obj):
    with open("plugins//storage//" + name, "wb") as file:
        pickle.dump(obj, file)


def syncfrom(name, default=None):
    try:
        with open("plugins//storage//" + name, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        syncto(name, default)
        return default
