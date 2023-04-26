import json
import os

def main(server_id, role_id):
    # Checks if the file path exists and if not, makes a .json file.
    if not os.path.exists(f"servers/{server_id}/permissions"):
        os.makedirs(f"servers/{server_id}/permissions")
        with open(f"servers/{server_id}/permissions/permissions.json", "w") as file:
                json.dump([], file)
    
    # Loads the permissions.json file as an array.
    with open(f"servers/{server_id}/permissions/permissions.json", "r") as file:
        manager_array = json.load(file)
    
    # Checks if arg1 is contained in that array, if not append it.
    if role_id in manager_array:
        return "That Role is already in the Manager Group!"
    else:
        manager_array.append(role_id)
    
        with open(f"servers/{server_id}/permissions/permissions.json", "w") as file:
            json.dump(manager_array, file)
        
        return "Added the role to the Manager Group."