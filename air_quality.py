import random

def get_air_quality():

    cities = {
        "الكويت": random.randint(70,150),
        "الدمام": random.randint(60,130),
        "المنامة": random.randint(40,100)
    }

    return cities
