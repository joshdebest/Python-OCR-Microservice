import os


def get_filename(filepath):
    # print("Get filename: " + os.path.splitext(os.path.basename(filepath))[0])
    return os.path.splitext(os.path.basename(filepath))[0]


def check_if_path_exists(directory_path):
    is_file = os.path.exists(directory_path)
    print("Does the path exist: " + str(is_file))
    if is_file:
        print("Path already exists")
    else:
        print("Creating new path")
        try:
            os.mkdir(directory_path)
        except OSError:
            print("Creation of the directory %s failed" % directory_path)
        else:
            print("Successfully created the directory %s " % directory_path)


def get_lien_type_from_template_path(file_path):
    filename_list = get_filename(file_path).split("-")
    filename_list.pop(0)
    return "-".join(filename_list)