def main(user_warner_roles, manager_array):

    # Checks if user has a role in the manager perms array
    for user_role_id in user_warner_roles:
        if str(user_role_id) in manager_array:
            return True
        else:
            continue
    return False