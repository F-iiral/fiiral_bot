import json
import os

def main(server_id, user_to_show):
    # Checks if the file path exists and if not, makes a .json file.
    if not os.path.exists(f"servers/{server_id}/warns"):
        os.makedirs(f"servers/{server_id}/warns")
        with open(f"servers/{server_id}/warns/warns.json", "w") as file:
                json.dump({}, file)
    
    # Loads the warns.json file as an array.
    with open(f"servers/{server_id}/warns/warns.json", "r") as file:
        warns_dict = json.load(file)
    
    try:
        warns = warns_dict[f"{user_to_show}"]
    except:
        warns = 0
    
    return f"The user currently has {warns} Warnings."