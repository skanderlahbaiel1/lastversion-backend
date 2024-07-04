"""
URL Configuration for the Application.

This module defines the URL patterns for the application. Each URL pattern is associated 
with a specific view function that handles the corresponding HTTP request. The URLs cover 
various functionalities including retrieving data, updating resources, and managing associations.

Usage:
    These URL patterns are automatically used by Django to route HTTP requests to the appropriate 
    view functions. Each pattern is mapped to a specific endpoint and a view function.

Examples:
    To add a new URL pattern, import the view function and add a path entry to the urlpatterns list:
    
    .. code-block:: python

        from . import views
        urlpatterns.append(path('new_endpoint/', views.new_view, name='new_view'))

Attributes:
    urlpatterns (list): A list of URL patterns to be matched against incoming requests.

Notes:
    - Ensure that the view functions referenced in the URL patterns are defined in the views module.
    - URL patterns can include parameters to capture parts of the URL and pass them to the view function.

URL Patterns:
    - '' : Home page, handled by `views.home`.
    - 'get_iotypes/' : Retrieve I/O types, handled by `views.get_iotypes`.
    - 'get_resources/' : Retrieve resources, handled by `views.get_resources`.
    - 'get_signals/' : Retrieve signals, handled by `views.get_signals`.
    - 'get_names/' : Retrieve resource names, handled by `views.get_names`.
    - 'get_boards/' : Retrieve boards, handled by `views.get_boards`.
    - 'get_infos_boards/' : Retrieve board information, handled by `views.get_infos_boards`.
    - 'get_interface/' : Retrieve interfaces, handled by `views.get_interface`.
    - 'get_infos_interfaces/' : Retrieve interface information, handled by `views.get_infos_interfaces`.
    - 'get_iosignals/' : Retrieve I/O signals, handled by `views.get_iosignals`.
    - 'get_associations/' : Retrieve associations, handled by `views.get_associations`.
    - 'get_connecteur/' : Retrieve connectors, handled by `views.get_connecteur`.
    - 'update_io/' : Update I/O details, handled by `views.update_io`.
    - 'delete_iotype/' : Delete an I/O type, handled by `views.delete_iotype`.
    - 'update_resource/' : Update a resource, handled by `views.update_resource`.
    - 'delete_ressourceCategory/' : Delete a resource category, handled by `views.delete_ressourceCategory`.
    - 'update_signal/' : Update a signal, handled by `views.update_signal`.
    - 'delete_signal/' : Delete a signal, handled by `views.delete_signal`.
    - 'update_name/' : Update a resource name, handled by `views.update_name`.
    - 'delete_name/' : Delete a resource name, handled by `views.delete_name`.
    - 'update_board/' : Update a board, handled by `views.update_board`.
    - 'delete_board/' : Delete a board, handled by `views.delete_board`.
    - 'update_interface/' : Update an interface, handled by `views.update_interface`.
    - 'delete_interface/' : Delete an interface, handled by `views.delete_interface`.
    - 'associate/' : Create an association, handled by `views.associate`.
    - 'delete_association/' : Delete an association, handled by `views.delete_association`.
    - 'update_iosignal/' : Update an I/O signal, handled by `views.update_iosignal`.
    - 'delete_iosignal/' : Delete an I/O signal, handled by `views.delete_iosignal`.
    - 'associate_connecteur/' : Associate a connector, handled by `views.associate_connecteur`.
    - 'get_connector/' : Retrieve a connector, handled by `views.get_connector`.
    - 'update_connector/' : Update a connector, handled by `views.update_connector`.
    - 'delete_connector/' : Delete a connector, handled by `views.delete_connector`.
    - 'update_interface_connector/' : Update an interface-connector relationship, handled by `views.update_interface_connector`.
    - 'delete_interface_connector/' : Delete an interface-connector relationship, handled by `views.delete_interface_connector`.
"""

from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),
    path('get_iotypes/',views.get_iotypes,name="get_iotypes"),
    path('get_resources/',views.get_resources,name="get_resources"),
    path('get_signals/',views.get_signals,name="get_signals"),
    path('get_names/',views.get_names,name="get_names"),
    path('get_boards/',views.get_boards,name="get_boards"),
    path('get_infos_boards/',views.get_infos_boards,name="get_infos_boards"),
    path('get_interface/',views.get_interface,name="get_interface"),
    path('get_infos_interfaces/',views.get_infos_interfaces,name="get_infos_interfaces"),
    path('get_iosignals/',views.get_iosignals,name="get_iosignals"),
    path('get_associations/',views.get_associations,name="get_associations"),
    path('get_connecteur/',views.get_connecteur,name="get_connecteur"),
    path('update_io/',views.update_io,name="update_io"),
    path('delete_iotype/',views.delete_iotype,name="delete_iotype"),
    path('update_resource/',views.update_resource,name="update_resource"),
    path('delete_ressourceCategory/',views.delete_ressourceCategory,name="delete_ressourceCategory"),
    path('update_signal/',views.update_signal,name="update_signal"),
    path('delete_signal/',views.delete_signal,name="delete_signal"),
    path('update_name/',views.update_name,name="update_name"),
    path('delete_name/',views.delete_name,name="delete_name"),
    path('update_board/',views.update_board,name="update_board"),
    path('delete_board/',views.delete_board,name="delete_board"),
    path('update_interface/',views.update_interface,name="update_interface"),
    path('delete_interface/',views.delete_interface,name="delete_interface"),
    path('associate/',views.associate,name="associate"),
    path('delete_association/',views.delete_association, name="delete_association"),
    path('update_iosignal/',views.update_iosignal,name="update_iosignal"),
    path('delete_iosignal/',views.delete_iosignal, name="delete_iosignal"),
    path('associate_connecteur/',views.associate_connecteur,name="associate_connecteur"),
    #path('delete_connecteur/',views.delete_connecteur, name="delete_connecteur"),
    path('get_connector/',views.get_connector,name="get_connector"),
    path('update_connector/', views.update_connector, name='update_connector'),
    path('delete_connector/', views.delete_connector, name='delete_connector'),
    path('update_interface_connector/', views.update_interface_connector, name='update_interface_connector'),
    path('create_signal/', views.create_signal, name='create_signal'), 
    path('get_assigned_resources/', views.get_assigned_resources, name='get_assigned_resources'),
    path('add_signal/', views.add_signal, name='add_signal'),
    path('update_signal/', views.update_signal, name='update_signal'),
    path('delete_signal/', views.delete_signal, name='delete_signal'),  
    path('update_matrix/', views.update_matrix, name='update_matrix'),
    path('get_assigned_resources/', views.get_assigned_resources, name='get_assigned_resources'),
    path('create_assigned_resource/', views.create_assigned_resource, name='create_assigned_resource'),
    path('delete_assigned_resource/', views.delete_assigned_resource, name='delete_assigned_resource'),
    path('update_assigned_resource/', views.update_assigned_resource, name='update_assigned_resource'),
]   