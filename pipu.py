"""
Updates all the outdated packages listed by executing 'pip list -o',
except the ones mentioned in exclude_list.

Handles the case when pip needs to be updated as well.
"""

import logging
import os
import shlex
import subprocess
import sys
import time

# skip following packages
exclude_list = {}
include_list = {"Installing", "Successfully"}


def print_last_n_lines(text, offset=10, starts_with=None):
    filtered = [
        line
        for line in text.splitlines()
        if starts_with is None or line.split(" ")[0] in starts_with
    ][-offset:]
    print("\n".join(filtered))


def execute_os_command(command):
    """Executes OS command and returns its output"""
    result = subprocess.check_output(
        shlex.split(command), 
        universal_newlines=True
    )
    time.sleep(1) # helps to get complete output
    return result


def print_skipped_packages(packages, exclude_list):
    """Prints skipped packages"""
    skipped_packages = packages.intersection(exclude_list)
    if skipped_packages:
        print(f"Skipped packages: {', '.join(skipped_packages)}")


def update_pip():
    pip_command = "python -m pip install --upgrade pip"

    print(f"Upgrading pip: {pip_command}")
    pip_output = execute_os_command(pip_command)
    print_last_n_lines(pip_output, 2, include_list)
    logging.debug(f"update_pip()\n{pip_output}")


def update_outdated_packages(package_list):
    update_command = f"pip install -U {package_list}"

    print(f"Updating outdated packages: {update_command}")
    update_output = execute_os_command(update_command)
    print_last_n_lines(update_output, 2, include_list)
    logging.debug(f"update_outdated_packages()\n{update_output}")


def list_outdated_packages(exclude_list):
    list_command = "pip list -o"

    print(f"Checking for outdated packages: {list_command}")
    list_output = execute_os_command(list_command)

    packages = {
        line.split(" ")[0] 
        for line in list_output.split("\n")[2:] 
        if line
    }
    
    logging.debug(f"list_outdated_packages()\n{packages}")
    print_skipped_packages(packages, exclude_list)
    return sorted(packages - exclude_list) if packages else None


def setup():
    logging_dir = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "logs")
    if not os.path.exists(logging_dir):
        os.mkdir(logging_dir)
    logging_log = os.path.splitext(os.path.basename(sys.argv[0]))[0] + ".log"
    logging.basicConfig(filename=os.path.join(logging_dir, logging_log), level=logging.DEBUG)


def update_from_env(l, ev):
    if ev in os.environ:
        e = set(os.environ[ev].split(","))
        return l.union(e) if l else e
    else:
        return l


def main():
    global exclude_list

    print("PIPU - PIP Updater, the latest version.")
    setup()
    exclude_list = update_from_env(exclude_list, "PIPU_EXCLUDE")
    packages = list_outdated_packages(exclude_list)
    
    if not packages:
        print("No packages to update!")
        return

    if "pip" in packages:
        update_pip()
        packages.pop(packages.index("pip"))

    if packages:
        update_outdated_packages(" ".join(packages))


if __name__ == '__main__':
    main()
