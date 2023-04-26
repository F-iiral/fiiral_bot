import random

###############
# Definitions #
###############
pi = 3.1415
phi = 1.6180
cur_system_worth = 5
mid_system_worth = 5
dev_system_worth = 5

#############
# Functions #
#############
def ordinal(n: int):
    if 11 <= (n % 100) <= 13:
        suffix = 'th'
    else:
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
    return str(n) + suffix
 
def get_planet_class(temperature):
    global cur_system_worth, mid_system_worth, dev_system_worth
    cur_system_worth += 1
    mid_system_worth += 1
    dev_system_worth += 1

    seed = random.random()
    
    if seed < 0.01:
        return "Type-A Supergiant"
    elif seed < 0.02:
        return "Type-H Supermassive World"
    elif seed < 0.12:
        if temperature >= 1000:
            return "Type-W Hot Giant"
        elif temperature < 125:
            return "Type-N Ice Giant"
        else:
            return "Type-J Gas Giant"
    elif seed < 0.25:
        if temperature >= 1000:
            return "Type-D Hot Dwarf"
        elif temperature < 125:
            return "Type-B Ice Dwarf"
        else:
            return "Type-S Gas Dwarf"
    elif seed < 0.9:
        if temperature >= 1000:
            return "Type-C Molten World"
        elif temperature >= 700:
            return "Type-M Hot World"
        elif temperature >= 375:
            return "Type-I Heated World"
        elif temperature >= 250:
            return "Type-L Lunar World"      
        elif temperature >= 125:
            return "Type-O Cold World"
        else:
            return "Type-P Frozen World"
    elif temperature > 200 and temperature < 400:
        mid_system_worth += 20
        dev_system_worth += 80
        return "Type-E Habitable World"
    else:
        mid_system_worth += 15
        dev_system_worth += 60
        return "Type-F Semihabitable World"

def get_moon_class(temperature):
    global cur_system_worth, mid_system_worth, dev_system_worth
    cur_system_worth += 1
    mid_system_worth += 1
    dev_system_worth += 1

    seed = random.random()

    if seed < 0.5:
        return ""
    elif seed < 0.55:
        return "Type-H Supermassive World"
    elif seed < 0.75:
        if temperature >= 1000:
            return "Type-D Hot Dwarf"
        elif temperature < 125:
            return "Type-B Ice Dwarf"
        else:
            return "Type-S Gas Dwarf"
    elif seed < 0.95:
        if temperature >= 1000:
            return "Type-C Molten World"
        elif temperature >= 700:
            return "Type-M Hot World"
        elif temperature >= 375:
            return "Type-I Heated World"
        elif temperature >= 250:
            return "Type-L Lunar World"      
        elif temperature >= 125:
            return "Type-O Cold World"
        else:
            return "Type-P Frozen World"
    elif temperature > 200 and temperature < 400:
        mid_system_worth += 10
        dev_system_worth += 40
        return "Type-E Habitable World"
    else:
        mid_system_worth += 7
        dev_system_worth += 28
        return "Type-F Semihabitable World"

def generate_system():
    seed = random.random()
    star_mass = 1/(seed * 10)
    
    if star_mass > 16:
        star_class = "O-Class Star"
    elif star_mass > 2.1:
        star_class = "B-Class Star"
    elif star_mass > 1.4:
        star_class = "A-Class Star"
    elif star_mass > 1.04:
        star_class = "F-Class Star"
    elif star_mass > 0.8:
        star_class = "G-Class Star"
    elif star_mass > 0.45:
        star_class = "K-Class Star"
    elif star_mass > 0.08:
        star_class = "M-Class Star"

    if star_mass > 55:
        star_luminosity = 32000 * star_mass
    elif star_mass > 2:
        star_luminosity = 1.4*star_mass ** 4
    elif star_mass > 0.45:
        star_luminosity = star_mass ** 4
    else:
        star_luminosity = 0.23 * star_mass ** 2.3
    
    star_array = [
        "Star Mass (Suns): " + str(round(star_mass, 3)),
        "Star Luminosity (Suns): " + str(round(star_luminosity, 3)),
        star_class,
        ""
    ]
    
    temp_star_array = generate_planets(star_luminosity, star_mass, seed)
    for element in temp_star_array:
        star_array.append(element)

    return star_array

def generate_planets(star_luminosity, star_mass, seed):
    global cur_system_worth, mid_system_worth, dev_system_worth
    
    first_planet_orbit = seed * star_mass
    temp_star_array = []
    
    for planet in range(0,20):
        planet_orbit = first_planet_orbit * phi ** planet
        planet_temperature = (star_luminosity / (pi * planet_orbit ** 2)) * 285 + 3  
        planet_class = get_planet_class(planet_temperature)

        if planet_orbit > star_mass * star_luminosity * 50:
            cur_system_worth -= 1
            if planet_class == "Type-E Habitable World":
                mid_system_worth -= 20
                dev_system_worth -= 80
            if planet_class == "Type-F Habitable World":
                mid_system_worth -= 15
                dev_system_worth -= 60
            break
        if planet_temperature > 2000:
            cur_system_worth -= 1
            continue
        if random.random() < 0.1:
            temp_star_array.append("Asteroid Belt")
            cur_system_worth += 2
            mid_system_worth += 4
            dev_system_worth += 6
            continue

        temp_star_array.append(planet_class)

        # Generate Moons
        temp_planet_array = generate_moons(seed, planet_temperature, planet_orbit)
        for element in temp_planet_array:
            temp_star_array.append(element)

    return temp_star_array

def generate_moons(seed, planet_temperature, planet_orbit):
    global cur_system_worth, mid_system_worth, dev_system_worth

    first_moon_orbit = seed
    temp_planet_array = []
    
    for moon in range(0,5):
        moon_orbit = first_moon_orbit * phi ** moon
        moon_temperature = planet_temperature
        moon_class = get_moon_class(moon_temperature)

        if seed > random.random():
            if moon_class == "Type-E Habitable World":
                mid_system_worth -= 10
                dev_system_worth -= 40
            if moon_class == "Type-F Habitable World":
                mid_system_worth -= 7
                dev_system_worth -= 28
            break
        if moon_orbit <= 0.0005:
            if moon_class == "Type-E Habitable World":
                mid_system_worth -= 10
                dev_system_worth -= 40
            if moon_class == "Type-F Habitable World":
                mid_system_worth -= 7
                dev_system_worth -= 28
            continue
        if moon_orbit > planet_orbit:
            if moon_class == "Type-E Habitable World":
                mid_system_worth -= 10
                dev_system_worth -= 40
            if moon_class == "Type-F Habitable World":
                mid_system_worth -= 7
                dev_system_worth -= 28
            break

        temp_planet_array.append([moon_class])
    
    return temp_planet_array

def main():
    global cur_system_worth, mid_system_worth, dev_system_worth
    pre_result = generate_system()
    pre_result.insert(0, "Current System Worth: " + str(cur_system_worth) + " ₠")
    pre_result.insert(1, "Colonized System Worth: " + str(mid_system_worth) + " ₠")
    pre_result.insert(2, "Developed System Worth: " + str(dev_system_worth) + " ₠")
    pre_result.insert(3, "")

    cur_system_worth = 5
    mid_system_worth = 5
    dev_system_worth = 5
    result = ""

    for item in pre_result:
        if item == [""]:
            continue
        elif isinstance(item, list):
            sub_array_string = '\n\t'.join(item)
            result += f"\t{sub_array_string}\n"
        else:
            result += f"{item}\n"
    


    return result