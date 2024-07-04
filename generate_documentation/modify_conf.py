"""
This script modifies the Sphinx `conf.py` and `index.rst` files to correctly 
configure the documentation build process for a Django project. 

It ensures that:
1. The necessary paths and settings for Django are added.
2. Required Sphinx extensions are included.
3. Unnecessary TODO settings are removed.
4. The HTML theme is updated.
5. The `modules` directive is added to `index.rst` for module documentation.

Steps Performed:
    1. Read and modify `conf.py` to:
       - Add the Django setup and `sys.path` modifications.
       - Ensure necessary Sphinx extensions are included.
       - Update `exclude_patterns` to exclude build artifacts.
       - Change the HTML theme to `sphinx_rtd_theme`.
       - Remove `todo_include_todos` if present.

    2. Read and modify `index.rst` to:
       - Add the `modules` directive under the `:caption: Contents:` section.

Usage:
    Simply run the script in an environment where the `BASE_DIR` environment variable 
    is set to the root directory of your project.

Examples:
    Assuming the `BASE_DIR` environment variable is set, run the script as follows:

    ```python
    python modify_sphinx_files.py
    ```

Possible Errors:
    - FileNotFoundError: If the `conf.py` or `index.rst` file is not found at the specified path.
    - IOError: If there are issues with reading from or writing to the `conf.py` or `index.rst` file.

Notes:
    - Ensure that the `BASE_DIR` environment variable is correctly set to the root directory 
      of your project before running this script.
    - This script assumes that the `conf.py` and `index.rst` files are located in the `docs` directory 
      under the project root.
    - It also ensures a brief wait time using `time.sleep(2)` after making modifications.
"""
import os
import time

work_dir = os.getenv("BASE_DIR")

# Modify conf.py
conf_path = os.path.join(work_dir, 'docs', 'conf.py')
with open(conf_path, 'r') as original:
    data = original.read()

# Prepend sys.path modification and Django setup
sys_path_mod = """
import os
import sys
import django

sys.path.insert(0, os.path.abspath('../MS-CHARAC-BACK'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'mapping.settings'

django.setup()

"""
if "django.setup()" not in data:
    data = sys_path_mod + data

# Ensure extensions and exclude_patterns are correctly modified
if "extensions = [" not in data:
    data += "\nextensions = ['sphinx.ext.autodoc', 'sphinx.ext.todo', 'sphinx.ext.viewcode']"
else:
    for ext in ["'sphinx.ext.autodoc'", "'sphinx.ext.todo'", "'sphinx.ext.viewcode'"]:
        if ext not in data:
            data = data.replace("extensions = [", f"extensions = [{ext}, ")

if "exclude_patterns = [" not in data:
    data += "\nexclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']"
else:
    for pattern in ["'_build'", "'Thumbs.db'", "'.DS_Store'"]:
        if pattern not in data:
            data = data.replace("exclude_patterns = [", f"exclude_patterns = [{pattern}, ")

# Update the HTML theme
data = data.replace("html_theme = 'alabaster'", "html_theme = 'sphinx_rtd_theme'")
# Remove 'todo_include_todos = True' if present
data = data.replace("todo_include_todos = True\n", "")
with open(conf_path, 'w') as modified:
    modified.write(data)

# Modify index.rst
index_path = os.path.join(work_dir, 'docs', 'index.rst')
with open(index_path, 'r') as original:
    lines = original.readlines()

insert_line = ':caption: Contents:'
insert_index = None

# Search for the caption line to insert after
for i, line in enumerate(lines):
    if insert_line in line:
        insert_index = i + 1
        break

if insert_index is not None and '   modules\n' not in lines:
    lines.insert(insert_index, '\n   modules\n')
    with open(index_path, 'w') as modified:
        modified.writelines(lines)
else:
    print(f"Warning: Did not find the line '{insert_line}' to insert 'modules' or 'modules' already present.")

time.sleep(2)
