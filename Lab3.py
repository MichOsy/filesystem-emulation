import json
import os
import time
import random


filesystem_path = "filesystem3.json"
current_location = "/"
current_user = None
filesystem = {
    "Contents": {
        "Admin Log": {
            "Contents": {
                "Registrations": [
                    {
                        "username": "admin",
                        "password": "af2er34yh",
                        "type": "admin"
                    },
                    {
                        "username": "john",
                        "password": "25nf16hsy",
                        "type": "user",
                        "questions": {},
                        "mistakes": 0
                    },
                    {
                        "username": "kevin",
                        "password": "gd2t9s7bt",
                        "type": "user",
                        "questions": {},
                        "mistakes": 0
                    }
                ]
            },
            "Attributes": {
                "Read": "admin",
                "Write": "admin",
                "Owner": "admin"
            }
        },
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
    if current_user["type"] == "admin":
        print("reg <username> <password> - Register user")
        print("unreg <username> - Delete user")
    if current_user["type"] == "user":
        print("question <question> & <answer> - Add new secret question with answer")
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
        password = input("Password: ")
        for user in filesystem["Contents"]["Admin Log"]["Contents"]["Registrations"]:
            if user["username"] == username and user["password"] == password:
                global current_user
                current_user = user
                correct_login = True
                break
        else:
            print("Wrong login and / or password, try again")


def register(choice):
    args = choice[4:].split(" ")
    if len(args) != 2:
        print("Wrong arguments")
        return
    username = args[0]
    password = args[1]
    if password.isdigit() or password.isalpha() or len(password) < 7:
        print("Password should contain at least one letter, one number "
              "and be 7 symbols or more")
        return
    for user in filesystem["Contents"]["Admin Log"]["Contents"]["Registrations"]:
        if user["username"] == username:
            print("Username already used")
            return
    filesystem["Contents"]["Admin Log"]["Contents"]["Registrations"].append({
        "username": username,
        "password": password,
        "type": "user",
        "questions": {},
        "mistakes": 0
    })


def unregister(username):
    for user in filesystem["Contents"]["Admin Log"]["Contents"]["Registrations"]:
        if user["username"] == username:
            filesystem["Contents"]["Admin Log"]["Contents"]["Registrations"].remove(user)
            break
    else:
        print("User doesn't exist")


def add_question(args):
    args = args.split(" & ")
    if len(args) != 2:
        print("Wrong arguments")
        return
    current_user["questions"][args[0]] = args[1]


def loop():
    global current_location
    start = time.time()
    while True:
        choice = input(f"{current_location}: ")
        if time.time() - start > 30 and current_user["type"] == "user":
            if not current_user["questions"]:
                print("Add secret questions!")
                start = time.time()
            else:
                qs = current_user['questions']
                q = random.choice(list(qs))
                answer = input(f"Answer question {q}:")
                if answer != qs[q]:
                    print("Wrong answer")
                    current_user["mistakes"] += 1
                    if current_user["mistakes"] >= 3:
                        print("Too many mistakes, account is unregistered")
                        unregister(current_user["username"])
                    login()
                    start = time.time()
                    current_location = '/'
                else:
                    print("Correct, you can continue working")

        if choice == "pwd":
            print(current_location)
        elif choice == "help":
            show_help()
        elif choice == "relog":
            login()
            start = time.time()
            current_location = '/'
        elif choice.startswith("reg ") and current_user["type"] == "admin":
            register(choice)
        elif choice.startswith("unreg ") and current_user["type"] == "admin":
            unregister(choice[6:])
        elif choice.startswith("question ") and current_user["type"] == "user":
            add_question(choice[9:])
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
