import json
import os


user_data = [
    {
        "username": "admin",
        "type": "admin"
    },
    {
        "username": "john",
        "type": "user"
    },
    {
        "username": "kevin",
        "type": "user"
    }
]

filesystem_path = "filesystem.json"
current_location = "/"
current_user = user_data[1]
filesystem = {
    "Contents": {
        "A": {
            "Contents": {
                "Downloads": {
                    "Contents": {},
                    "Attributes": {
                        "Read": "user",
                        "Write": "user",
                        "Owner": "admin"
                    }
                }
            },
            "Attributes": {
                "Read": "user",
                "Write": "user",
                "Owner": "admin"
            }
        },
        "B": {
            "Contents": {
                "Projects": {
                    "Contents": {},
                    "Attributes": {
                        "Read": "user",
                        "Write": "user",
                        "Owner": "admin"
                    }
                }
            },
            "Attributes": {
                "Read": "user",
                "Write": "user",
                "Owner": "admin"
            }
        },
        "C": {
            "Contents": {
                "Temp": {
                    "Contents": {},
                    "Attributes": {
                        "Read": "user",
                        "Write": "user",
                        "Owner": "admin"
                    }
                }
            },
            "Attributes": {
                "Read": "user",
                "Write": "user",
                "Owner": "admin"
            }
        },
    },
    "Attributes": {
        "Read": "user",
        "Write": "admin",
        "Owner": "admin"
    }
}


def load_filesystem():
    if os.path.exists(filesystem_path):
        with open(filesystem_path, "r") as file:
            global filesystem
            filesystem = json.load(file)
        os.remove(filesystem_path)


def save_filesystem():
    with open(filesystem_path, "w") as file:
        json.dump(filesystem, file, indent=4)


def show_help():
    print("\n--- Commands ---")
    print("pwd - View current location")
    print("ls - View contents of current folder")
    print("cd <directory> - Change current folder")
    print("mkdir <folder_name> - Create a new folder")
    print("edit <file_name> - Create/edit a file")
    print("cat <file_name> - View file content")
    print("rm <item_name> - Delete a folder or a file")
    print("chmod <item_name> <permissions> - Change permissions for a folder or a file")
    print("relog - Login again")
    print("help - Show commands")
    print("exit - Exit\n")


def get_current_location():
    location = filesystem
    for directory in current_location[1:].split("/"):
        if directory:
            location = location["Contents"][directory]
    return location


def list_contents():
    location = get_current_location()["Contents"]
    for item in location:
        attrs = location[item]["Attributes"]
        print(f"{item} {'directory' if isinstance(location[item]['Contents'], dict) else 'file'} "
              f"Read:{attrs['Read']} Write:{attrs['Write']} Owner:{attrs['Owner']}")


def change_directory(path):
    global current_location
    if path == "/":
        current_location = "/"
    elif path.startswith("/"):
        location = filesystem
        for directory in path[1:].split("/"):
            if directory and directory in location["Contents"]:
                if isinstance(location["Contents"][directory]["Contents"], dict):
                    location = location["Contents"][directory]
                else:
                    break
            else:
                break
        else:
            prev_location = current_location
            current_location = path
            if not check_permission("", "Read"):
                print("This action is not allowed")
                current_location = prev_location
                return
            return
    elif path == "../":
        current_location = "/" + "/".join(current_location[1:].split("/")[:-1])
        return
    else:
        if path in get_current_location()["Contents"]:
            if not check_permission(path, "Read"):
                print("This action is not allowed")
                return
            current_location = current_location + "/" + path
            if current_location.startswith("//"):
                current_location = current_location[1:]
            return
    print("Invalid argument")


def create_folder(folder_name):
    if not check_permission("", "Write"):
        print("This action is not allowed")
        return
    location = get_current_location()
    if folder_name not in location["Contents"]:
        location["Contents"][folder_name] = {
            "Contents": {},
            "Attributes": {
                "Read": "user",
                "Write": "user",
                "Owner": "admin" if current_user["type"] == "admin" else current_user["username"],
            }
        }
    else:
        print("Folder already exists")


def edit_file(args):
    location = get_current_location()
    args = args.split(" ")
    filename = args[0]
    if len(args) > 1:
        content = " ".join(args[1:])
    else:
        content = ""
    if filename not in location["Contents"]:
        location["Contents"][filename] = {
            "Contents": content,
            "Attributes": {
                "Read": "user",
                "Write": "user",
                "Owner": "admin" if current_user["type"] == "admin" else current_user["username"],
            }
        }
    else:
        if not check_permission(filename, "Write"):
            print("This action is not allowed")
            return
        location["Contents"][filename]["Contents"] = content


def cat(filename):
    if not check_permission(filename, "Read"):
        print("This action is not allowed")
        return
    location = get_current_location()["Contents"]
    if filename in location and isinstance(location[filename]["Contents"], str):
        print(location[filename]["Contents"])
    else:
        print("File doesn't exist")


def delete_item(item_name):
    if not check_permission(item_name, "Write"):
        print("This action is not allowed")
        return
    location = get_current_location()
    if item_name in location["Contents"]:
        del location["Contents"][item_name]
    else:
        print("Item doesn't exist")


def change_permissions(args):
    args = args.split(" ")
    filename = " ".join(args[:-1])
    if not check_permission(filename, "Write"):
        print("This action is not allowed")
        return
    permissions = args[-1]
    permissions = list(permissions)
    if len(permissions) != 2:
        print("Invalid permissions")
        return

    read, write = permissions
    for permission in [read, write]:
        if not permission.isdigit() or not 0 <= int(permission) <= 2:
            print("Invalid permissions")
            return

    location = get_current_location()["Contents"]
    if filename not in location:
        print("Item doesn't exist")
        return

    num_to_word = {
        "0": "user",
        "1": "owner",
        "2": "admin"
    }

    location[filename]["Attributes"]["Read"] = num_to_word[read]
    location[filename]["Attributes"]["Write"] = num_to_word[write]


def check_permission(filename, type_):
    location = get_current_location()
    if filename == "":
        attrs = location["Attributes"]
    else:
        if filename not in location["Contents"]:
            print("File doesn't exist")
            return False
        attrs = location["Contents"][filename]["Attributes"]

    if attrs[type_] == "user":
        return True
    elif attrs[type_] == "admin":
        if current_user["type"] == "admin":
            return True
        else:
            return False
    elif attrs[type_] == "owner":
        if current_user["username"] == attrs["Owner"]:
            return True
        else:
            return False
    return False


def login():
    correct_login = False
    while not correct_login:
        username = input("Username: ")
        for user in user_data:
            if user["username"] == username:
                global current_user
                current_user = user
                correct_login = True
                break


def loop():
    global current_location
    while True:
        choice = input(f"{current_location}: ")
        if choice == "pwd":
            print(current_location)
        elif choice == "help":
            show_help()
        elif choice == "relog":
            login()
            current_location = '/'
        elif choice == "ls":
            list_contents()
        elif choice.startswith("cd "):
            change_directory(choice[3:].strip())
        elif choice.startswith("mkdir "):
            create_folder(choice[6:].strip())
        elif choice.startswith("edit "):
            edit_file(choice[5:].strip())
        elif choice.startswith("cat "):
            cat(choice[4:].strip())
        elif choice.startswith("rm "):
            delete_item(choice[3:].strip())
        elif choice.startswith("chmod "):
            change_permissions(choice[6:].strip())
        elif choice == "exit":
            break
        else:
            print("Invalid command. To show all commands use 'help'.")


if __name__ == "__main__":
    load_filesystem()
    try:
        login()
        show_help()
        loop()
    except Exception as e:
        raise e
    finally:
        save_filesystem()
