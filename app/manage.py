#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """
    Run administrative tasks.

    This function sets the `DJANGO_SETTINGS_MODULE` environment variable to specify the 
    settings module for the Django project. It then attempts to import and execute Django's 
    command-line utility for administrative tasks.

    Environment Variables:
        DJANGO_SETTINGS_MODULE (str): Specifies the settings module to be used by Django. 
        It is set to 'mapping.settings' by default.

    Exceptions:
        ImportError: Raised if Django is not installed or not available on the 
        PYTHONPATH environment variable.

    Examples:
        To execute a Django management command, run this script from the command line:

        .. code-block:: bash

            $ python3 ./manage.py <command>

        Replace `<command>` with the desired administrative command, such as `runserver` 
        or `migrate`.

    Raises:
        ImportError: If Django is not installed or the `DJANGO_SETTINGS_MODULE` is not set 
        correctly.

    Notes:
        - This function is typically called automatically when the script is executed directly.
        - It ensures that the Django environment is properly set up before running 
          administrative tasks.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mapping.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
