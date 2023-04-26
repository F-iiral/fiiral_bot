import json
import os
import fiiral_checker_bot

def main(server_id, user_to_remove, user_warner_roles, amount_to_remove):
    # Checks if the file path exists and if not, makes a .json file.
    if not os.path.exists(f"servers/{server_id}/permissions"):
        os.makedirs(f"servers/{server_id}/permissions")
        with open(f"servers/{server_id}/permissions/permissions.json", "w") as file:
                json.dump([], file)
    
    # Checks if the file path exists and if not, makes a .json file.
    if not os.path.exists(f"servers/{server_id}/warns"):
        os.makedirs(f"servers/{server_id}/warns")
        with open(f"servers/{server_id}/warns/warns.json", "w") as file:
                json.dump({}, file)

    # Loads the permissions.json file as an array.
    with open(f"servers/{server_id}/permissions/permissions.json", "r") as file:
        manager_array = json.load(file)

    permission_flip = fiiral_checker_bot.main(user_warner_roles, manager_array)
    if permission_flip == True:
        # Loads the warns.json file as an dict.
        with open(f"servers/{server_id}/warns/warns.json", "r") as file:
            warns_dict = json.load(file)
        
        # Removes an entry from warns.
        if str(user_to_remove) not in warns_dict:
            warns_dict[str(user_to_remove)] = 0
        else:
            warns_dict[str(user_to_remove)] -= amount_to_remove
        
        # No Negative Warns
        if warns_dict[str(user_to_remove)] < 0:
            warns_dict[str(user_to_remove)] = 0

        with open(f"servers/{server_id}/warns/warns.json", "w") as file:
            json.dump(warns_dict, file)
        return f"Remove the specified amount of warnings."
    else:
        return "You need manager permissions (♦) to do this!"