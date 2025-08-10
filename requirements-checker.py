'''
Last update July 27, 2025

V1.1
debugged get_imported_modules for utf-8 errors
added installation of standard modules on start of file
solved for multiple entries in a line
AI code cleaning implemented
Auto directory detection implemented

V1.0
Base file
'''
import os, sys
import subprocess

#preconfig
#install standard modules
subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True)
subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)

core_utils = ['pkgutil', 'importlib', 'stdlib_list', 'regex']

for pkgs in core_utils:
    subprocess.run([sys.executable, '-m', 'pip', 'install'] + list([pkgs]))


import pkgutil
import importlib
import regex
from importlib.metadata import distributions
from pathlib import Path
from stdlib_list import stdlib_list
import ast

def is_valid_package_name(name):
    # Very basic check for invalid names
    return all(c.isalnum() or c in {'-', '_', '.'} for c in name) and not name.endswith(',')


def get_imported_modules(directory):
    """
    Extracts imported modules from all Python files in the given directory.
    """
    imported_modules = set()
    std_libs = set(stdlib_list(f"{sys.version_info.major}.{sys.version_info.minor}"))

    for py_file in Path(directory).rglob('*.py'):
        print(f"Checking {py_file} for modules")
        with open(py_file, 'r', encoding='utf-8') as file:
            try:
                tree = ast.parse(file.read(), filename=str(py_file))
            except SyntaxError as e:
                print(f"SyntaxError in {py_file}: {e}")
                continue

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    if is_valid_package_name(module):
                        imported_modules.add(module)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split('.')[0]
                    if is_valid_package_name(module):
                        imported_modules.add(module)

    # Filter out standard library modules
    filtered_packages = [pkg for pkg in imported_modules if pkg.lower() not in std_libs]
    return filtered_packages


def get_imported_modules_deprecated(directory):
    """
    Extracts imported modules from all Python files in the given directory.
    """
    imported_modules = set()
    
    # Get the list of standard library modules for current Python version
    std_libs = set(stdlib_list(f"{sys.version_info.major}.{sys.version_info.minor}"))

    # Traverse all Python files in the directory
    for py_file in Path(directory).rglob('*.py'):
        print(f"checking {py_file} for modules")
        with open(py_file, 'r', encoding='utf-8') as file:
            content = file.read()

        # Find all imported modules (simple approach)
        for line in content.splitlines():
            if line.startswith('import ') or line.startswith('from '):
                # Handle standard import and from-import cases
                print(line) #testing if it catches this, working
                parts = line.split()
                # print(parts)
                if len(parts) >= 2:
                    if is_valid_package_name(parts[1]):
                        imported_modules.add(parts[1].split('.')[0])
                    else:
                        print(f"{parts} is not a valid module")
    # Filter out standard library modules (some may have versions, strip them for check)
    filtered_packages = []
    for req in imported_modules:
        pkg_name = req.split('==')[0].lower()
        if pkg_name not in std_libs:
            filtered_packages.append(req)

    return filtered_packages


def create_requirements_file(imported_modules):
    """
    Creates a `requirements.txt` file based on the imported modules.
    """
    with open('requirements.txt', 'w', encoding='utf-8') as req_file:
        for module in imported_modules:
            req_file.write(module + '\n')


def install_missing_modules(imported_modules):
    """
    Installs missing modules using pip.
    """
    installed_modules = set(pkgutil.iter_modules())  # Get installed modules
    missing_modules = [module for module in imported_modules if module not in installed_modules]

    if missing_modules:
        print(f"Installing missing modules: {', '.join(missing_modules)}")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_modules)
    else:
        print("All modules are already installed.")


def install_missing_from_requirements(requirements_path='requirements.txt'):
    """
    Installs missing modules listed in requirements.txt using pip.
    """
    # # Get the list of standard library modules for current Python version
    # std_libs = set(stdlib_list(f"{sys.version_info.major}.{sys.version_info.minor}"))
    
    
    # Read packages from requirements.txt
    with open(requirements_path, 'r') as f:
        required_packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
    # # Filter out standard library modules (some may have versions, strip them for check)
    # filtered_packages = []
    # for req in required_packages:
    #     pkg_name = req.split('==')[0].lower()
    #     if pkg_name not in std_libs:
    #         filtered_packages.append(req)

    # Get installed packages (names normalized)
    installed_packages = {dist.metadata['Name'].lower() for dist in distributions()}

    # Identify missing packages (checking only package names, ignoring versions for simplicity)
    missing_packages = []
    for req in required_packages:
        pkg_name = req.split('==')[0].lower()
        if pkg_name not in installed_packages:
            missing_packages.append(req)
    
    not_valid = []
    if missing_packages:
        print(f"Installing missing modules from requirements.txt: {', '.join(missing_packages)}")
        
        #created a for loop to install each missing package to root out errors
        for missing in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + list([missing]))
            except:
                print(f"{missing} is not valid")
                not_valid.append(missing)
    
        print(f"following packages were not installed due to being invalid {not_valid}")
                
    else:
        print("All required modules from requirements.txt are already installed.")


def main():
    
    #detect current path and change the CWD
    path_file = os.path.realpath(__file__)
    #filename_1 = os.path.normcase(__file__)
    #filename_1
    head, tail = os.path.split(path_file)
    os.chdir(regex.search("(.+)"+tail,path_file)[1])
    path = head.replace("\\","/")+"/"
    
    print(f"setting {path} directory as default")
    
    directory = path
    
    # Get imported modules
    imported_modules = get_imported_modules(directory)
    print(f"Discovered modules: {imported_modules}")

    # Create requirements.txt
    create_requirements_file(imported_modules)
    print("requirements.txt has been created.")

    # Install missing modules
    try:
        install_missing_from_requirements()
    except:
        print("General error with requirements file.")


if __name__ == '__main__':
    main()

