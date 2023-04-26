import json
import os
import fiiral_checker_bot

def main(server_id, user_to_punish, user_warner_roles):
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
    
    # Loads the warns.json file as an array.
    with open(f"servers/{server_id}/warns/warns.json", "r") as file:
        warns_dict = json.load(file)

    # Loads the permissions.json file as an array.
    with open(f"servers/{server_id}/permissions/permissions.json", "r") as file:
        manager_array = json.load(file)

    permission_flip = fiiral_checker_bot.main(user_warner_roles, manager_array)
    if permission_flip == True:    
        try:
            warns = warns_dict[f"{user_to_punish}"]
        except:
            warns = 0
        
        return warns
    else:
        return None