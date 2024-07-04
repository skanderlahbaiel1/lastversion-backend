"""
This module configures the Django admin interface for the application. It imports and registers various models with the Django admin to enable CRUD (Create, Read, Update, Delete) operations via the admin panel. Each model registration enhances the admin interface by allowing administrators to manage database records for the application directly through a web interface.

Usage:
    This module is automatically used by Django's admin app to determine which models are available in the admin interface and how they are displayed. No further steps are required beyond importing this module in your admin.py file.

Modifications:
    You can customize the behavior of models in the admin by creating ModelAdmin classes and registering them with their respective models. See Django's documentation on ModelAdmin for more details: https://docs.djangoproject.com/en/stable/ref/contrib/admin/#django.contrib.admin.ModelAdmin

Models Registered:
    - Folder: Represents a folder in a file system (potentially virtual).
    - File: Represents a file contained within a Folder.
    - resources_categories: Categorizes various resources, potentially linking to io_types.
    - io_type: Defines types of I/O operations or resources.
    - assigned_resources: Links resources to specific tasks or uses in the system.
    - resource_name: Names a particular resource, giving it a unique identifier.
    - association: Represents a many-to-many relationship between resources and other elements in the system.
    - connecteur: Represents a physical or logical connector within the system.
    - interfaces: Defines various interfaces available within the system.
    - IO_list: Lists I/O operations or tasks.
    - contacts: Represents contact points or nodes in connecteurs.
    - link: Represents a link or connection between two interfaces.
    - wirings: Details the wiring configurations used within the system.
    - modele_io_mapping: Maps I/O models to various components or configurations within the system.

Examples:
    To add a model to the admin interface, simply import the model and use the `admin.site.register()` function:
    ```python
    from django.contrib import admin
    from .models import MyModel

    admin.site.register(MyModel)
    ```

Notes:
    - Ensure that each model has a unique representation in the admin; otherwise, it can be confusing to differentiate between similar records.
    - Use `list_display`, `search_fields`, and other `ModelAdmin` options to enhance admin interface usability.

Warnings:
    - Improper configuration of the admin can lead to security risks, e.g., exposing sensitive data or allowing unintended operations. Always restrict admin access using appropriate permissions.
"""




from django.contrib import admin

from .models import *

admin.site.register(Folder)
admin.site.register(File)
admin.site.register(resources_categories)
admin.site.register(io_type)
admin.site.register(assigned_resources)
admin.site.register(resource_name)
admin.site.register(association)
admin.site.register(connecteur)
admin.site.register(interfaces)
admin.site.register(IO_list)
admin.site.register(contacts)
admin.site.register(link)
admin.site.register(wirings)
admin.site.register(modele_io_mapping)
