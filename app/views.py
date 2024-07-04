# Create your views here.
from .models import *
#from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from django.views.decorators.http import require_http_methods
import json
import pdb
from django.forms.models import model_to_dict
import logging

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def home(request): 
    """
    Handle requests to the home page.

    This view function processes both GET and POST requests to the home page. It handles 
    the creation of folders and files based on the submitted form data and retrieves all 
    folders, I/O types, and resource categories to be displayed on the page.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object with the rendered home page.

    POST Handling:
        - If the request method is POST, it checks the form_name to determine the type of form submitted.
        - For 'file_form':
            - Retrieves or creates the specified folder.
            - Processes the uploaded files and saves them to the folder.
        - For 'folder_form':
            - Retrieves the folder name from the request.
            - Checks if a folder with the same name already exists.
            - Creates a new folder if it doesn't exist or handles the case where it already exists.
            - Redirects to the home page to avoid form resubmission on page refresh.

    Examples:
        - Submitting a 'file_form' with selected files:
            .. code-block:: python

                data = {
                    'form_name': 'file_form',
                    'selected-folder': 'Documents',
                    'files': [<file1>, <file2>]
                }
                response = client.post('/', data)

        - Submitting a 'folder_form' to create a new folder:
            .. code-block:: python

                data = {
                    'form_name': 'folder_form',
                    'folder_name': 'NewFolder'
                }
                response = client.post('/', data)

    Notes:
        - The view handles file uploads and folder creation.
        - It prevents folder name duplication by checking if a folder with the same name already exists.
        - Redirects after folder creation to avoid duplicate form submissions on page refresh.

    Returns:
        HttpResponse: The rendered home page with context data including folders, I/O types, and resource categories.
    """
    if request.method == 'POST':
        form_name = request.POST.get('form_name')
        if form_name == 'file_form':    
            folder_name = request.POST.get('selected-folder')
            folder, created = Folder.objects.get_or_create(folder_name=folder_name)
            files = request.FILES.getlist("files") 
            for file_path in files:        
                file_name = file_path.name 
                print(file_name)
                file_data = file_path.read()
                folder.files.create(file_name=file_name,data=file_data)
        if form_name == 'folder_form':
            folder_name = request.POST.get('folder_name', None)
            # Check if a folder with the same name already exists
            if not Folder.objects.filter(folder_name=folder_name).exists():
                # If not, create the folder
                Folder.objects.create(folder_name=folder_name)
            else:
                # Handle the case where the folder already exists
                print("Folder with the same name already exists!")

            # Redirect to avoid form resubmission on page refresh
            return redirect('home')   

    folders = Folder.objects.all()    
    io_types = io_type.objects.all()  
    resources = resources_categories.objects.all()
    return render(request,"home.html",{'folders':folders,"io_types":io_types,"resources":resources})


#récupérer les données des io types et les mettre dans notre ag-grid (reponse JSON)
def get_iotypes(request):
    """
    Retrieve all I/O types from the database and return them as a JSON response.

    This view function fetches all `io_type` objects from the database and constructs 
    a list of dictionaries representing each I/O type. Each dictionary contains the 
    keys 'ioType' and 'symbol' corresponding to the I/O type's name and symbol, respectively. 
    The resulting list is returned as a JSON response.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing a list of dictionaries, each representing an I/O type.

    Examples:
        Example JSON response:
        
        .. code-block:: json

            [
                {"ioType": "Type1", "symbol": "T1"},
                {"ioType": "Type2", "symbol": "T2"}
            ]

    Notes:
        - This view is typically used to provide data for an ag-Grid component in a web application.
        - The `safe` parameter in `JsonResponse` is set to `False` to allow serializing a list of dictionaries.

    """
    #récupérer les objets io_types de la base de données 
    io_types = io_type.objects.all()
    #créer une liste de dictionnaires à partir des objets 'io_types' pour l'introduire dans notre ag-grid. Chaque dict represente un tyoe d'IO avec les clés 'io type' et 'symbol'
    io_types_list  = [{'ioType':io_typ.io_type_name,'symbol':io_typ.io_type_symbol} for io_typ in io_types]
    return JsonResponse(io_types_list , safe=False)

def get_resources(request):
    """
    Retrieve all resource categories from the database and return them as a JSON response.

    This view function fetches all `resources_categories` objects from the database, 
    constructs a list of dictionaries representing each resource category, and returns 
    the list as a JSON response. Each dictionary contains the resource name, count, and 
    a list of associated I/O types.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing a list of dictionaries, each representing a resource category.

    Examples:
        Example JSON response:
        
        .. code-block:: json

            [
                {
                    "resourcename": "Resource1",
                    "count": 10,
                    "io type": ["IOType1", "IOType2"]
                },
                {
                    "resourcename": "Resource2",
                    "count": 5,
                    "io type": ["IOType3"]
                }
            ]

    Notes:
        - This view is typically used to provide data for an ag-Grid component in a web application.
        - The `safe` parameter in `JsonResponse` is set to `False` to allow serializing a list of dictionaries.

    """
    # Fetching the resources from the database
    resources = resources_categories.objects.all()
    # Preparing a list to hold resource data
    liste_resources = []
    for resource in resources:
        # Accessing the io_types and preparing a list of their names or ids
        io_types = list(resource.io_type.all().values_list('io_type_name', flat=True))
        # Building the dictionary for JSON response
        resource_dict = {
            'resourcename': resource.category,
            'count': resource.count,
            'io type': io_types,  # Now it's a list of strings which is serializable
        }
        liste_resources.append(resource_dict)

    # Returning the JsonResponse with the properly formatted list
    return JsonResponse(liste_resources, safe=False)

from django.db import IntegrityError

@csrf_exempt
def update_resource(request):
    """
    Update or create a resource category based on the provided data.

    This view function handles the updating or creation of a `resources_categories` 
    object. It processes the incoming JSON data, updates or creates the resource 
    category, associates the specified I/O types, and returns a JSON response 
    indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation. 
        On success, it includes the updated resource details.

    Examples:
        Example JSON request body:
        
        .. code-block:: json

            {
                "resourcename": "Resource1",
                "count": 10,
                "ioTypes": ["IOType1", "IOType2"]
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "Resource name updated successfully",
                "resource": {
                    "resourcename": "Resource1",
                    "count": 10,
                    "ioTypes": ["IOType1", "IOType2"]
                }
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It uses `get_or_create` to ensure the resource category exists.
        - The function associates the specified I/O types with the resource category.
        - It returns a detailed JSON response including the updated resource information on success.
        - On error, it returns a JSON response with the error message and a 500 status code.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        print("Received data:", data)  # Debugging output

        if request.method == "POST":
            resource, created = resources_categories.objects.get_or_create(category=data['resourcename'])
            if not created:
                return JsonResponse({"success": False, "message": "Resource category already exists"}, status=400)
        else:
            resource, created = resources_categories.objects.get_or_create(category=data['resourcename'])
            created = False  # Ensure 'created' is always defined

        resource.count = int(data.get('count', 0))  # Safeguard with a default value
        print("Resource fetched or created:", resource.category, "Created:", created)  # Debugging output

        io_type_ids = data.get('ioTypes', [])
        io_types = io_type.objects.filter(io_type_name__in=io_type_ids)

        if io_types.count() != len(io_type_ids):
            missing_io_types = set(io_type_ids) - set(io_types.values_list('io_type_name', flat=True))
            return JsonResponse({"success": False, "message": f"Some I/O types do not exist: {', '.join(missing_io_types)}"}, status=400)

        resource.io_type.set(io_types)
        print("IO Types set for resource.")  # Debugging output

        resource.save()

        resource_updated = {
            'resourcename': resource.category,
            'count': resource.count,
            'ioTypes': [io.io_type_name for io in resource.io_type.all()]
        }
        return JsonResponse({"success": True, "message": 'Resource name updated successfully', 'resource': resource_updated})
    except json.JSONDecodeError as e:
        print("Error decoding JSON data:", str(e))  # Output error to console or logs
        return JsonResponse({"success": False, "message": "Invalid JSON data: " + str(e)}, status=400)
    except resources_categories.DoesNotExist as e:
        print("Resource category does not exist:", str(e))  # Output error to console or logs
        return JsonResponse({"success": False, "message": "Resource category does not exist: " + str(e)}, status=404)
    except io_type.DoesNotExist as e:
        print("I/O type does not exist:", str(e))  # Output error to console or logs
        return JsonResponse({"success": False, "message": "I/O type does not exist: " + str(e)}, status=404)
    except IntegrityError as e:
        print("Integrity error during update_resource:", str(e))  # Output error to console or logs
        return JsonResponse({"success": False, "message": "Resource category already exists"}, status=400)
    except Exception as e:
        print("General error during update_resource:", str(e))  # Output error to console or logs
        return JsonResponse({"success": False, "message": "An unexpected error occurred: " + str(e)}, status=500)


    
def delete_ressourceCategory(request):
    """
    Delete a resource category based on the provided data.

    This view function handles the deletion of a `resources_categories` object. It processes 
    the incoming JSON data to identify the resource category to delete, performs the deletion, 
    and returns a JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation. 
        On success, it includes a success message.

    Examples:
        Example JSON request body:
        
        .. code-block:: json

            {
                "resourcename": "Resource1"
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "Resource category deleted successfully"
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It fetches the `resources_categories` object by the provided category name.
        - The `delete` method is called on the fetched object, which will cascade and 
          delete related entries if the ForeignKey is set with `on_delete=models.CASCADE`.
        - On error, it returns a JSON response with the error message and a 500 status code.
    """
    try:
        data = json.loads(request.body.decode('utf-8'))
        category = resources_categories.objects.get(category=data['resourcename'])
        category.delete()  # This will cascade and delete related entries if your ForeignKey is set with on_delete=models.CASCADE
        return JsonResponse({"success": True, "message": 'Resource category deleted successfully'})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
    
# récupérer les io types associés à une resource
def get_io_res(resource):
    """
    Retrieve the I/O types associated with a given resource.

    This function fetches all `io_type` objects associated with the provided 
    resource, formats them into a list of their names, and returns the list.

    Args:
        resource (resources_categories): The resource category for which to retrieve associated I/O types.

    Returns:
        list: A list of I/O type names associated with the provided resource.

    Examples:
        Assuming `resource` is an instance of `resources_categories`:

        .. code-block:: python

            resource = resources_categories.objects.get(category='Resource1')
            io_types = get_io_res(resource)
            print(io_types)  # Output: ['IOType1', 'IOType2']

    Notes:
        - The function uses a reverse relationship lookup to find `io_type` objects associated with the given resource.
        - The returned list contains only the names of the I/O types.
    """
    #récupérer des objets io types associées à cette resource
    ioTypes = io_type.objects.filter(resources__in=[resource])
    #formatter çà sous format de liste des noms
    liste_io = [io.io_type_name for io in ioTypes]

    return liste_io

@csrf_exempt
@require_POST
def update_matrix(request):
    """
    Update the matrix for a specific interfaceConnector.

    Args:
        request (HttpRequest): The HTTP request object containing the matrix data and connector name.

    Returns:
        JsonResponse: A JSON response indicating success or failure.
    """
    try:
        # Extract data from the request body
        data = json.loads(request.body)
        connector_name = data.get('connector_name')
        matrix = data.get('matrix')

        if connector_name is None or matrix is None:
            return JsonResponse({'error': 'Connector name and matrix data are required.'}, status=400)

        # Retrieve the interfaceConnector instance
        connector = interfaceConnector.objects.get(connecteur__name=connector_name)

        # Update the matrix field
        connector.set_matrix(matrix)

        return JsonResponse({'message': 'Matrix updated successfully.'})

    except interfaceConnector.DoesNotExist as e:
        logger.error(f"interfaceConnector not found: {e}")
        return JsonResponse({'error': 'interfaceConnector not found.'}, status=404)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON: {e}")
        return JsonResponse({'error': 'Invalid JSON.'}, status=400)
    except KeyError as e:
        logger.error(f"Missing key in data: {e}")
        return JsonResponse({'error': f'Missing key: {e}'}, status=400)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
def get_signals(request):
    """
    Retrieve all signals from the database and return them as a JSON response.

    This view function fetches all `Signal` objects from the database, 
    constructs a list of dictionaries representing each signal, and returns the list 
    as a JSON response. Each dictionary contains details about the signal, including 
    the signal name.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing a list of dictionaries, each representing a signal.

    Examples:
        Example JSON response:
        
        .. code-block:: json

            [
                {
                    "name": "Signal1"
                },
                {
                    "name": "Signal2"
                }
            ]

    Notes:
        - This view is typically used to provide data for components in a web application.
        - The `safe` parameter in `JsonResponse` is set to `False` to allow serializing a list of dictionaries.
    """
    # Retrieve all signals
    signals = Signal.objects.all()

    # Create a list of dictionaries to be serialized to JSON
    signal_list = [
        {
            'name': signal.name,
        }
        for signal in signals
    ]

    return JsonResponse(signal_list, safe=False)

@csrf_exempt
@require_http_methods(["GET", "POST", "DELETE"])
def assigned_resources_view(request):
    if request.method == "GET":
        return get_assigned_resources(request)
    elif request.method == "POST":
        return create_assigned_resource(request)
    elif request.method == "DELETE":
        return delete_assigned_resource(request)

def get_assigned_resources(request):
    """
    Retrieve all assigned resources from the database and return them as a JSON response.

    This view function fetches all `assigned_resources` objects from the database,
    constructs a list of dictionaries representing each assigned resource, and returns
    the list as a JSON response. Each dictionary contains details about the assigned
    resource, including the signal name, board internal mapping, I/O type, and category.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing a list of dictionaries, each representing an assigned resource.

    Examples:
        Example JSON response:

        .. code-block:: json

            [
                {
                    "signal": "Signal1",
                    "board_internal_mapping": "Mapping1",
                    "io_type": ["IOType1"],
                    "category": "Category1"
                },
                {
                    "signal": "Signal2",
                    "board_internal_mapping": "Mapping2",
                    "io_type": ["IOType2"],
                    "category": "Category2"
                }
            ]
    """
    resources = assigned_resources.objects.all()
    resource_list = [
        {
            'signal': resource.signal.name,
            'board_internal_mapping': resource.board_internal_mapping,
            'io_type': [resource.io_type.io_type_name] if resource.io_type else [],
            'category': resource.category.category
        }
        for resource in resources
    ]
    return JsonResponse(resource_list, safe=False)

@csrf_exempt
@require_http_methods(["POST"])
def create_assigned_resource(request):
    """
    Create a new assigned resource in the database based on the provided data.

    This view function processes the incoming JSON data, creates a new `assigned_resources` object,
    and returns a JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation. 
        On success, it includes the details of the created assigned resource.

    Examples:
        Example JSON request body for creating an assigned resource:

        .. code-block:: json

            {
                "signal_name": "Signal1",
                "board_internal_mapping": "Mapping1",
                "ioType": ["IOType1"],
                "resource": "Category1"
            }

        Example JSON response on success:

        .. code-block:: json

            {
                "success": True,
                "message": "Assigned resource created successfully.",
                "assigned_resource": {
                    "signal": "Signal1",
                    "board_internal_mapping": "Mapping1",
                    "io_type": "IOType1",
                    "category": "Category1"
                }
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
    """
    try:
        data = json.loads(request.body)
        
        if 'signal_name' not in data:
            return JsonResponse({'success': False, 'message': 'Signal name is missing.'}, status=400)
        signal_name = data.get('signal_name')
        
        if signal_name is None:
            return JsonResponse({'success': False, 'message': 'Signal name is None.'}, status=400)

        signal_name = signal_name.strip()  # Ensure no leading/trailing spaces
        
        board_internal_mapping = data.get('board_internal_mapping')
        io_type_name = data.get('ioType')
        category_name = data.get('resource')

        print(f"Received data: {data}")  # Log the received data for debugging

        signal = Signal.objects.get(name__iexact=signal_name)  # Case insensitive search
        io_type_instance = io_type.objects.get(io_type_name=io_type_name[0]) if io_type_name else None
        category = resources_categories.objects.get(category=category_name)

        assigned_resource = assigned_resources.objects.create(
            signal=signal,
            board_internal_mapping=board_internal_mapping,
            io_type=io_type_instance,
            category=category
        )

        response_data = {
            'signal': assigned_resource.signal.name,
            'board_internal_mapping': assigned_resource.board_internal_mapping,
            'io_type': assigned_resource.io_type.io_type_name if assigned_resource.io_type else None,
            'category': assigned_resource.category.category
        }
        return JsonResponse({'success': True, 'message': 'Assigned resource created successfully.', 'assigned_resource': response_data})

    except Signal.DoesNotExist:
        print("Signal not found.")
        return JsonResponse({'success': False, 'message': 'Signal not found.'}, status=400)
    except io_type.DoesNotExist:
        print("IO type not found.")
        return JsonResponse({'success': False, 'message': 'IO type not found.'}, status=400)
    except resources_categories.DoesNotExist:
        print("Category not found.")
        return JsonResponse({'success': False, 'message': 'Category not found.'}, status=400)
    except json.JSONDecodeError:
        print("Invalid JSON.")
        return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_assigned_resource(request):
    """
    Delete assigned resources from the database based on the provided signal name.

    This view function deletes all `assigned_resources` objects that match the provided
    signal name in the request body. It returns a JSON response indicating the success
    or failure of the operation.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.

    Examples:
        Example JSON request body for deleting assigned resources:

        .. code-block:: json

            {
                "signal_name": "Signal1"
            }

        Example JSON response on success:

        .. code-block:: json

            {
                "success": True,
                "message": "Assigned resources deleted successfully."
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
    """
    try:
        data = json.loads(request.body)
        signal_name = data.get('signal_name')

        if not signal_name:
            return JsonResponse({'success': False, 'message': 'Signal name is required.'}, status=400)

        try:
            assigned_resources.objects.filter(signal__name=signal_name).delete()
            return JsonResponse({'success': True, 'message': 'Assigned resources deleted successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=500)
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["PUT"])
def update_assigned_resource(request):
    """
    Update an existing assigned resource in the database based on the provided data.

    This view function processes the incoming JSON data, updates the specified `assigned_resources` object,
    and returns a JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.
        On success, it includes the details of the updated assigned resource.

    Examples:
        Example JSON request body for updating an assigned resource:

        .. code-block:: json

            {
                "signal_name": "Signal1",
                "board_internal_mapping": "Mapping1",
                "ioType": ["IOType1"],
                "resource": "Category1"
            }

        Example JSON response on success:

        .. code-block:: json

            {
                "success": True,
                "message": "Assigned resource updated successfully.",
                "assigned_resource": {
                    "signal": "Signal1",
                    "board_internal_mapping": "Mapping1",
                    "io_type": "IOType1",
                    "category": "Category1"
                }
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
    """
    try:
        data = json.loads(request.body)
        print(f"Received data: {data}")  # Debugging

        if 'signal_name' not in data or 'resource' not in data or 'board_internal_mapping' not in data:
            print("Missing required fields.")
            return JsonResponse({'success': False, 'message': 'Missing required fields.'}, status=400)

        signal_name = data['signal_name']
        board_internal_mapping = data['board_internal_mapping']
        io_type_name = data['ioType']
        category_name = data['resource']

        print(f"Signal name: {signal_name}")
        print(f"Board internal mapping: {board_internal_mapping}")
        print(f"IO type name: {io_type_name}")
        print(f"Category name: {category_name}")

        try:
            signal = Signal.objects.get(name__iexact=signal_name)  # Case insensitive search
        except Signal.DoesNotExist:
            print("Signal not found.")
            return JsonResponse({'success': False, 'message': 'Signal not found.'}, status=400)

        try:
            io_type_instance = io_type.objects.get(io_type_name=io_type_name[0]) if io_type_name else None
        except io_type.DoesNotExist:
            print("IO type not found.")
            return JsonResponse({'success': False, 'message': 'IO type not found.'}, status=400)

        try:
            category = resources_categories.objects.get(category=category_name)
        except resources_categories.DoesNotExist:
            print("Category not found.")
            return JsonResponse({'success': False, 'message': 'Category not found.'}, status=400)

        try:
            # Find the assigned resource to update
            assigned_resource = assigned_resources.objects.get(
                signal=signal,
                category=category
            )
        except assigned_resources.DoesNotExist:
            print("Assigned resource not found.")
            return JsonResponse({'success': False, 'message': 'Assigned resource not found.'}, status=400)
        except assigned_resources.MultipleObjectsReturned:
            print("Multiple assigned resources found.")
            return JsonResponse({'success': False, 'message': 'Multiple assigned resources found.'}, status=400)

        # Update fields
        assigned_resource.board_internal_mapping = board_internal_mapping
        assigned_resource.io_type = io_type_instance

        assigned_resource.save()

        response_data = {
            'signal': assigned_resource.signal.name,
            'board_internal_mapping': assigned_resource.board_internal_mapping,
            'io_type': assigned_resource.io_type.io_type_name if assigned_resource.io_type else None,
            'category': assigned_resource.category.category
        }
        print(f"Updated assigned resource: {response_data}")  # Debugging
        return JsonResponse({'success': True, 'message': 'Assigned resource updated successfully.', 'assigned_resource': response_data})

    except json.JSONDecodeError:
        print("Invalid JSON.")
        return JsonResponse({'success': False, 'message': 'Invalid JSON.'}, status=400)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

#récupérer les noms (type) de ressources dans l'io assignation
def get_names(request): 
    """
    Retrieve all resource names from the database and return them as a JSON response.

    This view function fetches all `resource_name` objects from the database, 
    constructs a list of dictionaries representing each resource name, and 
    returns the list as a JSON response. Each dictionary contains the resource type.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing a list of dictionaries, each representing a resource name.

    Examples:
        Example JSON response:
        
        .. code-block:: json

            [
                {
                    "resource type": "ResourceType1"
                },
                {
                    "resource type": "ResourceType2"
                }
            ]

    Notes:
        - This view is typically used to provide data for an ag-Grid component in a web application.
        - The `safe` parameter in `JsonResponse` is set to `False` to allow serializing a list of dictionaries.
    """
    #récupérer les noms de ressources (comme les type des ressources ayant la même caractéristique
    # électrique (tension, intensité .......))
    noms_resources = resource_name.objects.all()
    #créer une liste des dictionnaires pour l'introduire dans notre ag-grid
    liste_noms = [{'resource type':nom.name} for nom in noms_resources]
    return JsonResponse(liste_noms, safe=False)  

#récupérer les cartes dans l'io assignation
def get_boards(request):
    """
    Retrieve all boards from the database and return them as a JSON response.

    This view function fetches all `boards` objects from the database, constructs 
    a list of dictionaries representing each board, and returns the list as a JSON response. 
    Each dictionary contains the board name.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing a list of dictionaries, each representing a board.

    Examples:
        Example JSON response:
        
        .. code-block:: json

            [
                {
                    "board": "Board1"
                },
                {
                    "board": "Board2"
                }
            ]

    Notes:
        - This view is typically used to provide data for an ag-Grid component in a web application.
        - The `safe` parameter in `JsonResponse` is set to `False` to allow serializing a list of dictionaries.
    """
    #récupérer les cartes (représente la connexion entre les cartes.......))
    all_boards = boards.objects.all()
    #créer une liste des dictionnaires pour l'introduire dans notre ag-grid
    list_boards = [{'board':board.board} for board in all_boards]
    return JsonResponse(list_boards, safe=False)  

#récupérer les cartes pour les utiliser afin de definir nos interfaces
# cette fonction sert particulièrement à faciliter le choix des interfaces 
def get_infos_boards(request):
    """
    Retrieve board information to facilitate the selection of interfaces and return it as a JSON response.

    This view function fetches all `boards` objects from the database, constructs 
    two lists of dictionaries representing the boards, and returns them in a JSON 
    response. Each list represents boards for different selection purposes.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing two lists of dictionaries, each representing a board for different purposes.

    Examples:
        Example JSON response:
        
        .. code-block:: json

            {
                "liste board 1": [
                    {"Board 1": "Board1"},
                    {"Board 1": "Board2"}
                ],
                "liste board 2": [
                    {"Board 2": "Board1"},
                    {"Board 2": "Board2"}
                ]
            ]

    Notes:
        - This view is designed to facilitate the selection of interfaces by providing 
          board information in two separate lists.
        - The `safe` parameter in `JsonResponse` is set to `False` to allow serializing a dictionary containing lists.
    """
    # Retrieve boards data
    all_boards = boards.objects.all()

    # Create lists to hold board information
    list_board1 = [{'Board 1':board.board} for board in all_boards]
    list_board2 = [{'Board 2':board.board} for board in all_boards]

    # Create JSON response
    infos_json = {
        "liste board 1":list_board1,
        "liste board 2":list_board2
    }
    return JsonResponse(infos_json, safe=False) 

def get_interface(request):
    """
    Retrieve all interfaces from the database and return them as a JSON response.

    This view function fetches all `interfaces` objects from the database, constructs 
    a list of dictionaries representing each interface, and returns the list as a JSON response. 
    Each dictionary contains details about the boards, interface name, and connectors.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing a list of dictionaries, each representing an interface.

    Examples:
        Example JSON response:
        
        .. code-block:: json

            [
                {
                    "board1": "Board1",
                    "board2": "Board2",
                    "interfaceName": "Board1-Board2",
                    "connectors": ["Connector1", "Connector2"]
                },
                {
                    "board1": "Board3",
                    "board2": "Board4",
                    "interfaceName": "Board3-Board4",
                    "connectors": ["Connector3"]
                }
            ]

    Notes:
        - This view is typically used to provide data for an ag-Grid component in a web application.
        - The `safe` parameter in `JsonResponse` is set to `False` to allow serializing a list of dictionaries.
    """
    try:
        all_interfaces = interfaces.objects.all()
        data = []

        for interface in all_interfaces:
            connectors = interfaceConnector.objects.filter(interface=interface).values_list('connecteur__name', flat=True)
            data.append({
                'board1': interface.board1.board,
                'board2': interface.board2.board,
                'interfaceName': interface.interface,
                'connectors': list(connectors)
            })

        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# import logging
# logger = logging.getLogger(__name__)

# def get_interfaces(request):
#     try:
#         # Retrieve interfaces data
#         interfaces_data = interfaces.objects.all()

#         # Create a list of dictionaries for introducing into our ag-grid
#         liste_interfaces = []
#         for interface in interfaces_data:
#             board1_name = interface.board1.board if interface.board1 else None
#             board2_name = interface.board2.board if interface.board2 else None
#             interface_name = f"{board1_name}-{board2_name}"
#             interface_dict = model_to_dict(interface)
#             interface_dict['board1'] = board1_name
#             interface_dict['board2'] = board2_name
#             interface_dict['interface_name'] = interface_name
#             liste_interfaces.append(interface_dict)

#         return JsonResponse(liste_interfaces, safe=False)
#     except Exception as e:
#         # Log the error for debugging purposes
#         logger.error(f"Error occurred in get_interfaces view: {e}")
#         # Return an error response
#         return JsonResponse({'error': 'An error occurred while processing the request.'}, status=500)
    
#récupérer les interfaces et les noms de ressources pour après les associer 
# cette fonction sert particulièrement à faciliter le choix des interfaces et noms de ressources assoicés
def get_infos_interfaces(request):
    """
    Retrieve interfaces and resource names from the database and return them as a JSON response.

    This view function fetches all `interfaces` and `resource_name` objects from the database, 
    constructs lists of dictionaries representing each interface and resource name, and returns 
    them in a JSON response.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing two lists of dictionaries, one for interfaces 
        and one for resource names.

    Examples:
        Example JSON response:
        
        .. code-block:: json

            {
                "liste noms": [
                    {"resource type": "ResourceType1"},
                    {"resource type": "ResourceType2"}
                ],
                "liste interfaces": [
                    {"interface": "Interface1"},
                    {"interface": "Interface2"}
                ]
            ]

    Notes:
        - This view is typically used to provide data for an ag-Grid component in a web application.
        - The `safe` parameter in `JsonResponse` is set to `False` to allow serializing a dictionary containing lists.
    """
    #récupérer les interfaces (représente la connexion entre les cartes.......))
    nom_interfaces = interfaces.objects.all()
    #créer une liste des dictionnaires pour l'introduire dans notre ag-grid
    liste_interfaces = [{'interface':interface.interface} for interface in nom_interfaces]
    #récupérer les noms de ressources (comme les type des ressources ayant la même caractéristique
    # électrique (tension, intensité .......))
    noms_resources = resource_name.objects.all()
    #créer une liste des dictionnaires pour l'introduire dans notre sélecteur d'ag_grid ag-grid
    liste_noms = [{'resource type':nom.name} for nom in noms_resources]
    infos_json = {
        "liste noms":liste_noms,
        "liste interfaces":liste_interfaces
    }
    return JsonResponse(infos_json, safe=False) 
#count???


#récupérer les signaux dans les interfaces dans l'io assignation
def get_iosignals(request):
    """
    Retrieve all I/O signals from the database and return them as a JSON response.

    This view function fetches all `assigned_resources` objects from the database, constructs 
    a list of dictionaries representing each I/O signal, and returns the list as a JSON response. 
    Each dictionary contains details about the interface, resource name, signal number, signal name, 
    from/to information, source destination board, description, and nature.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing a list of dictionaries, each representing an I/O signal.

    Examples:
        Example JSON response:
        
        .. code-block:: json

            [
                {
                    "interface": "Interface1",
                    "resource name": "Resource1",
                    "signal number": 1,
                    "signal name": "Signal1",
                    "from/to": "From1/To1",
                    "source destination board": "Board1",
                    "description": "Description1",
                    "nature": "Nature1"
                },
                {
                    "interface": "Interface2",
                    "resource name": "Resource2",
                    "signal number": 2,
                    "signal name": "Signal2",
                    "from/to": "From2/To2",
                    "source destination board": "Board2",
                    "description": "Description2",
                    "nature": "Nature2"
                }
            ]

    Notes:
        - This view is typically used to provide data for an ag-Grid component in a web application.
        - The `safe` parameter in `JsonResponse` is set to `False` to allow serializing a list of dictionaries.
    """
    #récupérer les signaux dans les interfaces (représente les signaux qui existe dans les interfaces.......))
    signaux = assigned_resources.objects.all()
    #créer une liste des dictionnaires pour l'introduire dans notre ag-grid
    liste_signaux = [{'interface':signal.interface_resource.interface.interface,'resource name':signal.interface_resource.resource.name,'signal number':signal.resource_number, 'signal name':signal.signal_name,'from/to':signal.from_to,'source destination board':signal.source_destination_board,'description':signal.description,'nature':signal.nature} for signal in signaux]
    return JsonResponse(liste_signaux, safe=False) 

#récupérer les associations entre interfaces et les resources types dans l'io assignation
def get_associations(request):
    """
    Retrieve all associations between interfaces and resource types from the database and return them as a JSON response.

    This view function fetches all `association` objects from the database, constructs a list 
    of dictionaries representing each association, and returns the list as a JSON response. 
    Each dictionary contains details about the interface, resource type, and count of resources.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing a list of dictionaries, each representing an association.

    Examples:
        Example JSON response:
        
        .. code-block:: json

            [
                {
                    "interface": "Interface1",
                    "resource type": "ResourceType1",
                    "count": 20
                },
                {
                    "interface": "Interface2",
                    "resource type": "ResourceType2",
                    "count": 15
                }
            ]

    Notes:
        - This view is typically used to provide data for an ag-Grid component in a web application.
        - The `safe` parameter in `JsonResponse` is set to `False` to allow serializing a list of dictionaries.
    """
    #récupérer les associations (par exemple il y 20 de signaux de type DSI_LEGACY dans l'interface CIOC-ICB.......))
    associations = association.objects.all()
    #créer une liste des dictionnaires pour l'introduire dans notre ag-grid
    liste_associations = [{'interface':assoc.interface.interface,'resource type':assoc.resource.name,'count':assoc.nombre_resource} for assoc in associations]
    return JsonResponse(liste_associations, safe=False)     


# def get_connecteur(request):
#     list_connecteurs = None
#     if request.method == "POST":
#         data = json.loads(request.body.decode('utf-8'))
#         interface_name = data.get('interface')
#         if not interface_name:
#                 return JsonResponse({"error": "Missing 'interface' field in the request data."}, status=400)
#         interface_obj = interfaces.objects.get(interface=interface_name)
#         connecteurs = connecteur.objects.filter(interface=interface_obj)
#         list_connecteurs = [{'row':connect.dimension_row,'column':connect.dimension_column} for connect in connecteurs]
#     return JsonResponse(list_connecteurs,safe=False)

def get_connecteur(request):
    """
    Retrieve connectors associated with a specified interface and return them as a JSON response.

    This view function fetches `connecteur` objects associated with a specified interface from 
    the database, constructs a list of dictionaries representing each connector, and returns 
    the list as a JSON response. Each dictionary contains the row and column dimensions of the connector.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing a list of dictionaries, each representing a connector.

    Examples:
        Example JSON request body:
        
        .. code-block:: json

            {
                "interface": "Interface1"
            }

        Example JSON response:
        
        .. code-block:: json

            [
                {
                    "row": 10,
                    "column": 5
                },
                {
                    "row": 8,
                    "column": 4
                }
            ]

    Notes:
        - This view expects a POST request with a JSON body containing the `interface` field.
        - The `safe` parameter in `JsonResponse` is set to `False` to allow serializing a list of dictionaries.
    """
    list_connecteurs = None
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        interface_name = data.get('interface', '')
        if interface_name:
            interface_obj = interfaces.objects.get(interface=interface_name)
            connecteurs = connecteur.objects.filter(interface=interface_obj)
            list_connecteurs = [{'row': connect.dimension_row, 'column': connect.dimension_column} for connect in connecteurs]
    return JsonResponse(list_connecteurs, safe=False)



@require_http_methods(["GET"])
def get_connector(request):
    """
    Retrieve connector details based on a specified ID or return all connectors if no ID is specified.

    This view function fetches a `connector` object from the database based on the provided 
    ID and returns its details as a JSON response. If no ID is specified, it returns a list 
    of all connectors. Each dictionary in the response contains the name, row dimension, 
    and column dimension of the connector.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing the details of a specific connector or 
        a list of all connectors.

    Examples:
        Example JSON request with ID:
        
        .. code-block:: http

            GET /get_connector?id=1 HTTP/1.1

        Example JSON response for a specific connector:
        
        .. code-block:: json

            {
                "success": True,
                "connector": {
                    "name": "Connector1",
                    "row_dim": 10,
                    "column_dim": 5
                }
            }

        Example JSON response for all connectors:
        
        .. code-block:: json

            {
                "success": True,
                "connectors": [
                    {
                        "name": "Connector1",
                        "row_dim": 10,
                        "column_dim": 5
                    },
                    {
                        "name": "Connector2",
                        "row_dim": 8,
                        "column_dim": 4
                    }
                ]
            }

    Notes:
        - This view expects a GET request with an optional `id` query parameter.
        - If the `id` parameter is provided, the view returns the details of the specified connector.
        - If no `id` parameter is provided, the view returns a list of all connectors.
        - On error, the view returns a JSON response with an appropriate error message and status code.
    """
    connector_id = request.GET.get('id')
    if connector_id:
        try:
            connector_obj = connector.objects.get(id=connector_id)
            connector_data = {
                "name": connector_obj.name,
                "row_dim": connector_obj.row_dim,
                "column_dim": connector_obj.column_dim
            }
            return JsonResponse({"success": True, "connector": connector_data})
        except ObjectDoesNotExist:
            return JsonResponse({"success": False, "message": "Connector not found"}, status=404)
    else:
        connectors = connector.objects.all()
        connectors_data = [{
            "name": connector_obj.name,
            "row_dim": connector_obj.row_dim,
            "column_dim": connector_obj.column_dim
        } for connector_obj in connectors]
        return JsonResponse({"success": True, "connectors": connectors_data})

@csrf_exempt
@require_http_methods(["POST", "PUT"])
def update_connector(request):
    """
    Create or update a connector based on the provided data.

    This view function handles the creation or updating of a `connector` object. It processes 
    the incoming JSON data, updates or creates the connector, and returns a JSON response 
    indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation. 
        On success, it includes the details of the created or updated connector.

    Examples:
        Example JSON request body for creating or updating a connector:
        
        .. code-block:: json

            {
                "name": "Connector1",
                "row_dim": 10,
                "column_dim": 5
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "Connector created successfully.",
                "connector": {
                    "name": "Connector1",
                    "row_dim": 10,
                    "column_dim": 5
                }
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It uses `update_or_create` to ensure the connector exists or creates a new one if it does not.
        - On error, it returns a JSON response with the error message and a 500 status code.
    """
    data = json.loads(request.body.decode('utf-8'))
    name = data.get('name')
    row_dim = data.get('row_dim')
    column_dim = data.get('column_dim')

    try:
        connector_obj, created = connector.objects.update_or_create(
            name=name,
            defaults={'row_dim': row_dim, 'column_dim': column_dim}
        )
        message = 'Connector created successfully.' if created else 'Connector updated successfully.'
        return JsonResponse({"success": True, "message": message, 'connector': {'name': connector_obj.name, 'row_dim': connector_obj.row_dim, 'column_dim': connector_obj.column_dim}})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_connector(request):
    """
    Delete a connector based on the provided data.

    This view function handles the deletion of a `connector` object. It processes 
    the incoming JSON data to identify the connector to delete and returns a 
    JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.

    Examples:
        Example JSON request body for deleting a connector:
        
        .. code-block:: json

            {
                "name": "Connector1"
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "Connector deleted successfully."
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It fetches the `connector` object by the provided name and deletes it.
        - On error, it returns a JSON response with the error message and a 404 status code if the connector is not found.
    """
    data = json.loads(request.body.decode('utf-8'))
    name = data.get('name')
    try:
        connector_obj = connector.objects.get(name=name)
        connector_obj.delete()
        return JsonResponse({"success": True, "message": "Connector deleted successfully."})
    except connector.DoesNotExist:
        return JsonResponse({"success": False, "message": "Connector not found."}, status=404)
     
              
# def update_io(request):
#     if request.method == 'POST':
#         data = json.loads(request.body.decode('utf-8'))
#         io, created = io_type.objects.get_or_create(io_type_name=data['ioType'])
#         io.io_type_symbol = data['symbol']
#         io.save()
#         action = "created" if created else "updated"
#         return JsonResponse({"success": True, "message": f'IO type {action} successfully.', 'io': {'ioType': io.io_type_name, 'symbol': io.io_type_symbol}})


def update_io(request):
    """
    Create or update an I/O type based on the provided data.

    This view function handles the creation or updating of an `io_type` object. 
    It processes the incoming JSON data to either create a new I/O type or update an existing one 
    and returns a JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation. 
        On success, it includes the details of the created or updated I/O type.

    Examples:
        Example JSON request body for creating an I/O type:
        
        .. code-block:: json

            {
                "ioType": "IOType1",
                "symbol": "Symbol1"
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "IO type created successfully.",
                "io": {
                    "ioType": "IOType1",
                    "symbol": "Symbol1"
                }
            }

        Example JSON request body for updating an I/O type:
        
        .. code-block:: json

            {
                "ioType": "IOType1",
                "symbol": "NewSymbol"
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "IO type updated successfully.",
                "io": {
                    "ioType": "IOType1",
                    "symbol": "NewSymbol"
                }
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It uses `get_or_create` to ensure the I/O type exists or creates a new one if it does not.
        - On error, it returns a JSON response with an appropriate error message and status code.
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        io, created = io_type.objects.get_or_create(io_type_name=data['ioType'])
        io.io_type_symbol = data['symbol']
        io.save()
        return JsonResponse({"success": True, "message": 'IO type created successfully.', 'io': {'ioType': io.io_type_name, 'symbol': io.io_type_symbol}})

    elif request.method == 'PUT':
        data = json.loads(request.body.decode('utf-8'))
        try:
            io = io_type.objects.get(io_type_name=data['ioType'])
            io.io_type_symbol = data['symbol']
            io.save()
            return JsonResponse({"success": True, "message": 'IO type updated successfully.', 'io': {'ioType': io.io_type_name, 'symbol': io.io_type_symbol}})
        except io_type.DoesNotExist:
            return JsonResponse({"success": False, "message": "IO type not found."}, status=404)

def delete_iotype(request):
    """
    Delete an I/O type based on the provided data.

    This view function handles the deletion of an `io_type` object. It processes 
    the incoming JSON data to identify the I/O type to delete and returns a 
    JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.

    Examples:
        Example JSON request body for deleting an I/O type:
        
        .. code-block:: json

            {
                "ioType": "IOType1"
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "IO type deleted successfully."
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It fetches the `io_type` object by the provided I/O type name and deletes it.
        - On error, it returns a JSON response with an appropriate error message and status code.
    """
    if request.method == "DELETE":
        data = json.loads(request.body.decode('utf-8'))
        io_type.objects.get(io_type_name=data['ioType']).delete()

    return JsonResponse({"success":True,"message":'io type deleted successfully'},safe=False) 

from django.http import JsonResponse
import json


def update_signal(request):
    """
    Update a signal based on the provided data.

    This view function handles the updating of an `assigned_resources` object. 
    It processes the incoming JSON data to update the signal's attributes and returns a 
    JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation. 
        On success, it includes the details of the updated signal.

    Examples:
        Example JSON request body for updating a signal:
        
        .. code-block:: json

            {
                "signal_name": "Signal1",
                "resource": "Resource1",
                "board_internal_mapping": "NewMapping",
                "commentaire": "NewComment",
                "io_type": "IOTypeName",
                "io_index": "1"
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "Signal updated successfully.",
                "signal": {
                    "resource": "Resource1",
                    "signal_name": "Signal1",
                    "board_internal_mapping": "NewMapping",
                    "commentaire": "NewComment",
                    "io_type": "IOTypeName",
                    "io_index": "1"
                }
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It retrieves the corresponding `assigned_resources` object based on the provided signal name.
        - The signal's attributes are updated with the provided data, and the signal is saved.
        - The function returns a detailed JSON response including the updated signal information on success.
        - On error, it returns a JSON response with an appropriate error message and status code.
    """
    if request.method == "PUT":
        try:
            data = json.loads(request.body.decode('utf-8'))
            print("Received data:", data)

            # Attempt to fetch the signal object
            signal = assigned_resources.objects.get(signal_name=data['signal_name'])
            print("Signal found:", signal)

            # Update signal attributes if provided in the data
            if 'resource' in data:
                resource = resources_categories.objects.get(category=data['resource'])
                signal.category = resource

            if 'signal_name' in data:
                signal.signal_name = data['signal_name']

            if 'board_internal_mapping' in data:
                signal.board_internal_mapping = data['board_internal_mapping']

            if 'commentaire' in data:
                signal.commentaire = data['commentaire']

            if 'io_type' in data and data['io_type']:
                io_type_obj = io_type.objects.get(io_type_name=data['io_type'])
                signal.io_type = io_type_obj

            if 'io_index' in data:
                signal.io_index = data['io_index']

            signal.save()
            print("Signal updated:", signal)

            # Prepare updated signal information for response
            signal_updated = {
                'signal_name': signal.signal_name,
                'resource': signal.category.category,
                'board_internal_mapping': signal.board_internal_mapping,
                'commentaire': signal.commentaire,
                'io_type': signal.io_type.io_type_name if signal.io_type else '',
                'io_index': signal.io_index
            }
            return JsonResponse({"success": True, "message": 'Signal updated successfully', 'signal': signal_updated})

        except assigned_resources.DoesNotExist:
            return JsonResponse({"success": False, "message": "Signal does not exist."}, status=404)
        except resources_categories.DoesNotExist:
            return JsonResponse({"success": False, "message": "Resource category does not exist."}, status=404)
        except io_type.DoesNotExist:
            return JsonResponse({"success": False, "message": "IO type does not exist."}, status=404)
        except Exception as e:
            print("An error occurred:", str(e))
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

def create_signal(request):
    """
    Create a new signal based on the provided data.

    This view function handles the creation of an `assigned_resources` object. 
    It processes the incoming JSON data to create a new signal and returns a 
    JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation. 
        On success, it includes the details of the created signal.

    Examples:
        Example JSON request body for creating a signal:
        
        .. code-block:: json

            {
                "resource": "Resource1",
                "signal_name": "NewSignalName",
                "board_internal_mapping": "NewMapping",
                "commentaire": "NewComment",
                "ioType": "NewIOType",
                "ioIndex": "1",
                "resourceFPGA": "NewResourceFPGA"
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "Signal created successfully.",
                "signal": {
                    "resource": "Resource1",
                    "signal_name": "NewSignalName",
                    "board_internal_mapping": "NewMapping",
                    "io_type": "NewIOType",
                    "io_index": "NewIOIndex"
                }
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It retrieves the corresponding `resources_categories` object based on the provided resource name.
        - It creates a new `assigned_resources` object with the provided data.
        - The function returns a detailed JSON response including the created signal information on success.
        - On error, it returns a JSON response with an appropriate error message and status code.
    """
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

    print("create_signal endpoint hit")
    try:
        data = json.loads(request.body.decode('utf-8'))
        print("Received data:", data)

        # Attempt to fetch the resource category
        resource = resources_categories.objects.get(category=data['resource'])
        print("Resource category found:", resource)

        # Attempt to fetch the io_type object using io_type_name
        io_type_obj = io_type.objects.get(io_type_name=data['ioType'])
        print("IO type found:", io_type_obj)

        # Create a new signal object
        signal = assigned_resources(
            signal_name=data['signal_name'],
            category=resource,
            board_internal_mapping=data['board_internal_mapping'],
            #commentaire=data.get('commentaire', ''),
            io_type=io_type_obj,
            #io_index=data['ioIndex']
        )
        signal.save()
        print("Signal created:", signal)

        # Prepare created signal information for response
        signal_created = {
            'signal_name': signal.signal_name,
            'resource': resource.category,
            'board_internal_mapping': signal.board_internal_mapping,
            'io_type': io_type_obj.io_type_name,  # Assuming io_type model has a 'io_type_name' field
            #'io_index': signal.io_index,
            'resourceFPGA': data.get('resourceFPGA', '')
        }
        return JsonResponse({"success": True, "message": 'Signal created successfully', 'signal': signal_created})

    except resources_categories.DoesNotExist:
        return JsonResponse({"success": False, "message": "Resource category does not exist."}, status=404)
    except io_type.DoesNotExist:
        return JsonResponse({"success": False, "message": "IO type does not exist."}, status=404)
    except KeyError as e:
        return JsonResponse({"success": False, "message": f"Missing field: {str(e)}"}, status=400)
    except Exception as e:
        print("An error occurred:", str(e))
        return JsonResponse({"success": False, "message": str(e)}, status=500)

def delete_signal(request):
    """
    Delete a signal based on the provided data.

    This view function handles the deletion of `assigned_resources` objects. 
    It processes the incoming JSON data to identify the signals to delete and returns a 
    JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.

    Examples:
        Example JSON request body for deleting a signal:
        
        .. code-block:: json

            {
                "signal_name": "Signal1"
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "Signal(s) deleted successfully."
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It fetches the `assigned_resources` objects by the provided signal name and deletes them.
        - On error, it returns a JSON response with an appropriate error message and status code.
    """
    if request.method == "DELETE":
        try:
            data = json.loads(request.body.decode('utf-8'))
            print("Received data for deletion:", data)  # Logging received data

            signal_name = data.get('signal_name')
            if not signal_name:
                return JsonResponse({"success": False, "message": "Signal name not provided."}, status=400)

            signals = assigned_resources.objects.filter(signal_name=signal_name)
            if not signals.exists():
                return JsonResponse({"success": False, "message": "Signal does not exist."}, status=404)

            signals.delete()
            return JsonResponse({"success": True, "message": "Signal(s) deleted successfully."})

        except KeyError as e:
            print("KeyError:", str(e))  # Logging the KeyError
            return JsonResponse({"success": False, "message": f"Key error: {str(e)}"}, status=400)
        except json.JSONDecodeError as e:
            print("JSONDecodeError:", str(e))  # Logging the JSON decode error
            return JsonResponse({"success": False, "message": f"JSON decode error: {str(e)}"}, status=400)
        except Exception as e:
            print("Exception:", str(e))  # Logging any other exceptions
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

#ajouter des noms de resources 
def update_name(request):
    """
    Add a new resource name based on the provided data.

    This view function handles the creation of a `resource_name` object. 
    It processes the incoming JSON data to create a new resource name and 
    returns a JSON response indicating success.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success of the operation.

    Examples:
        Example JSON request body for adding a new resource name:
        
        .. code-block:: json

            {
                "resource type": "ResourceType1"
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "Resource name added successfully."
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It creates a new `resource_name` object with the provided resource type.
        - The function always returns a success message on completion.
    """
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
         # Create a new resource name object with the provided name
        resource_name.objects.create(name=data['resource type'])

    return JsonResponse({"success":True,"message":'resource name added successfully'},safe=False)  

def delete_name(request):
    """
    Delete a resource name based on the provided data.

    This view function handles the deletion of a `resource_name` object. 
    It processes the incoming JSON data to identify the resource name to delete and 
    returns a JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.

    Examples:
        Example JSON request body for deleting a resource name:
        
        .. code-block:: json

            {
                "resource type": "ResourceType1"
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "Resource name deleted successfully."
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It fetches the `resource_name` object by the provided resource type and deletes it.
        - On error, it returns a JSON response with an appropriate error message and status code.
    """
    if request.method == "DELETE":
        data = json.loads(request.body.decode('utf-8'))
        resource_name.objects.get(name=data['resource type']).delete()

    return JsonResponse({"success":True,"message":'ressource deleted successfully'},safe=False) 

#ajouter des cartes
def update_board(request):
    """
    Add or update a board based on the provided data.

    This view function handles the creation or updating of a `boards` object. 
    It processes the incoming JSON data to either create a new board or update an existing one 
    and returns a JSON response indicating success.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success of the operation.

    Examples:
        Example JSON request body for adding or updating a board:
        
        .. code-block:: json

            {
                "board": "Board1"
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "Board added successfully."
            }

        Example JSON response on update:
        
        .. code-block:: json

            {
                "success": True,
                "message": "Board updated successfully."
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It uses `update_or_create` to ensure the board exists or creates a new one if it does not.
        - The function returns a message indicating whether the board was created or updated.
    """
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        board_name = data['board']
        board, created = boards.objects.update_or_create(
            board=board_name, 
            defaults={'board': board_name}  # Assuming the model only has 'board' field.
        )
        if created:
            message = 'Board added successfully'
        else:
            message = 'Board updated successfully'
        return JsonResponse({"success": True, "message": message}, safe=False)

    
def delete_board(request):
    """
    Delete a board based on the provided data.

    This view function handles the deletion of a `boards` object. 
    It processes the incoming JSON data to identify the board to delete and 
    returns a JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.

    Examples:
        Example JSON request body for deleting a board:
        
        .. code-block:: json

            {
                "board": "Board1"
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "Board deleted successfully."
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It fetches the `boards` object by the provided board name and deletes it.
        - On error, it returns a JSON response with an appropriate error message and status code.
    """
    if request.method == "DELETE":
        data = json.loads(request.body.decode('utf-8'))
        boards.objects.get(board=data['board']).delete()
        #boards.objects.delete(board=data['board'])

    return JsonResponse({"success":True,"message":'board deleted successfully'},safe=False) 

# #ajouter des interfaces
# def update_interface(request):
#     if request.method == "POST":
#         data = json.loads(request.body.decode('utf-8'))
#         interfaces.objects.create(interface=data['interface'])

#     return JsonResponse({"success":True,"message":'interface added successfully'},safe=False) 

@csrf_exempt
def update_interface(request):
    """
    Add or update an interface based on the provided data.

    This view function handles the creation or updating of an `interfaces` object.
    It processes the incoming JSON data to either create a new interface or update an existing one
    and returns a JSON response indicating success.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success of the operation.

    Examples:
        Example JSON request body for adding or updating an interface:

        .. code-block:: json

            {
                "board1": "Board1",
                "board2": "Board2",
                "connectors": ["Connector1", "Connector2"]
            }

        Example JSON response on success:

        .. code-block:: json

            {
                "success": True,
                "message": "Interface updated successfully."
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - The function always returns a success message on completion.
    """
    if request.method in ["POST", "PUT"]:
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        if 'board1' not in data or 'board2' not in data or 'connectors' not in data:
            return JsonResponse({"error": "Missing 'board1', 'board2' or 'connectors' key in JSON data"}, status=400)

        if data['board1'] == data['board2']:
            return JsonResponse({"error": "board1 and board2 cannot be the same"}, status=400)

        try:
            board1_instance = boards.objects.get(board=data['board1'])
            board2_instance = boards.objects.get(board=data['board2'])
            connector_instances = connector.objects.filter(name__in=data['connectors'])
            if connector_instances.count() != len(data['connectors']):
                return JsonResponse({"error": "One or more connectors do not exist"}, status=400)
        except boards.DoesNotExist:
            print("Board does not exist")
            return JsonResponse({"error": f"One of the boards {data['board1']} or {data['board2']} does not exist"}, status=400)

        interface_name = f"{data['board1']}-{data['board2']}"

        if request.method == "POST":
            if interfaces.objects.filter(interface=interface_name).exists():
                print("Interface already exists")
                return JsonResponse({"error": f"Interface {interface_name} already exists"}, status=400)
            
            interface_instance, created = interfaces.objects.get_or_create(
                interface=interface_name,
                defaults={'board1': board1_instance, 'board2': board2_instance}
            )

            interface_connector_instances = [
                interfaceConnector(interface=interface_instance, connecteur=connector_instance)
                for connector_instance in connector_instances
            ]
            interfaceConnector.objects.bulk_create(interface_connector_instances, ignore_conflicts=True)

            return JsonResponse({"success": True, "message": "Interface created successfully"}, safe=False)

        elif request.method == "PUT":
            try:
                interface_instance = interfaces.objects.get(interface=interface_name)
                connector_names = data['connectors']
                connector_instances = connector.objects.filter(name__in=connector_names)

                # Delete existing connectors for the interface
                interfaceConnector.objects.filter(interface=interface_instance).delete()

                # Create new connectors for the interface
                interface_connector_instances = [
                    interfaceConnector(interface=interface_instance, connecteur=connector_instance)
                    for connector_instance in connector_instances
                ]
                interfaceConnector.objects.bulk_create(interface_connector_instances, ignore_conflicts=True)

                return JsonResponse({"success": True, "message": "Interface updated successfully"}, safe=False)
            except interfaces.DoesNotExist:
                return JsonResponse({"error": f"Interface {interface_name} does not exist"}, status=404)

    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)





from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def delete_interface(request):
    """
    Delete an interface based on the provided data.

    This view function handles the deletion of an `interfaces` object. 
    It processes the incoming JSON data to identify the interface to delete and 
    returns a JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.

    Examples:
        Example JSON request body for deleting an interface:
        
        .. code-block:: json

            {
                "interface": "Interface1"
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "Interface deleted successfully."
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It fetches the `interfaces` object by the provided interface name and deletes it.
        - On error, it returns a JSON response with an appropriate error message and status code.
    """
    if request.method == "DELETE":
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        if 'interface' not in data:
            return JsonResponse({"error": "Missing 'interface' key in JSON data"}, status=400)

        try:
            interface_instance = interfaces.objects.get(interface=data['interface'])
            interface_instance.delete()
            return JsonResponse({"success": True, "message": "Interface deleted successfully"}, safe=False)
        except interfaces.DoesNotExist:
            return JsonResponse({"error": f"Interface {data['interface']} does not exist"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)

def update_iosignal(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))

            # Fetching the assigned_resource using signal_name and category
            assigned_resource = assigned_resources.objects.get(
                signal_name=data['signal name'],
                category__category=data['resource name']  # Access category through the foreign key relationship
            )

            # Assuming an existing IO_list instance needs to be updated
            io_signal, created = IO_list.objects.update_or_create(
                assigned_resource=assigned_resource,
                defaults={
                    'from_to': data.get('from/to', ''),
                    'source_destination_board': data.get('source destination board', ''),
                    'description': data.get('description', ''),
                    'nature': data.get('nature', '')
                }
            )

            return JsonResponse({"success": True, "message": "Signal updated successfully", "created": created})

        except assigned_resources.DoesNotExist:
            return JsonResponse({"success": False, "message": "Assigned resource not found"}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method"}, status=400)

    

#ajouter des associations
def associate(request):
    """
    Add an association between an interface and a resource type based on the provided data.

    This view function handles the creation of an `association` object. 
    It processes the incoming JSON data to create a new association between an interface 
    and a resource type and returns a JSON response indicating success.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success of the operation.

    Examples:
        Example JSON request body for adding an association:
        
        .. code-block:: json

            {
                "interface": "Interface1",
                "resource type": "ResourceType1",
                "count": 20
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "We associated an interface with a resource type."
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It retrieves the `interfaces` and `resource_name` objects based on the provided data.
        - It creates a new `association` object with the specified interface, resource type, and count.
        - The function always returns a success message on completion.
    """
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))

        # Retrieve the interface and resource type objects based on the received data
        interface = interfaces.objects.get(interface=data['interface'])
        resource_type = resource_name.objects.get(name=data['resource type'])
        association.objects.create(resource=resource_type,interface=interface,nombre_resource=int(data['count']))

    return JsonResponse({"success":True,"message":'we associated an interface with a resource type'},safe=False)      

def delete_association(request):
    """
    Delete an association based on the provided data.

    This view function handles the deletion of an `association` object. 
    It processes the incoming JSON data to identify the association to delete and 
    returns a JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.

    Examples:
        Example JSON request body for deleting an association:
        
        .. code-block:: json

            {
                "association": "Association1"
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "Association deleted successfully."
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It fetches the `association` object by the provided association identifier and deletes it.
        - On error, it returns a JSON response with an appropriate error message and status code.
    """
    if request.method == "DELETE":
        data = json.loads(request.body.decode('utf-8'))
        association.objects.get(association=data['association']).delete()

    return JsonResponse({"success":True,"message":'association deleted successfully'},safe=False)   

def update_iosignal(request):
    """
    Update an I/O signal based on the provided data.

    This view function handles the updating of an `assigned_resources` object. 
    It processes the incoming JSON data to update the signal's attributes and returns a 
    JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.

    Examples:
        Example JSON request body for updating an I/O signal:
        
        .. code-block:: json

            {
                "interface": "Interface1",
                "resource name": "Resource1",
                "signal number": 1,
                "signal name": "NewSignalName",
                "from/to": "From1/To1",
                "source destination board": "Board1",
                "description": "NewDescription",
                "nature": "NewNature"
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "Signal updated successfully."
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It retrieves the `interfaces` and `resource_name` objects based on the provided data.
        - It updates the attributes of the `assigned_resources` object and saves it.
        - The function always returns a success message on completion.
    """
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))

        # Retrieve necessary objects from the database based on the received data
        interface = interfaces.objects.get(interface=data['interface'])
        resource = resource_name.objects.get(name=data['resource name'])
        interface_resource = association.objects.get(resource=resource,interface=interface)
        signal = assigned_resources.objects.get(signal_number=int(data['signal number']),interface_resource=interface_resource)
        
        # Update the signal object with the new data
        signal.signal_name = data['signal name']
        signal.from_to = data['from/to']
        signal.source_destination_board = data['source destination board']
        signal.description = data['description']
        signal.nature = data['nature']

        # Save the changes to the signal object in the database
        signal.save()

    return JsonResponse({"success": True,"message":'signal updated successfully'},safe=False)

def delete_iosignal(request):
    """
    Delete an I/O signal based on the provided data.

    This view function handles the deletion of an `assigned_resources` object. 
    It processes the incoming JSON data to identify the signal to delete and 
    returns a JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.

    Examples:
        Example JSON request body for deleting an I/O signal:
        
        .. code-block:: json

            {
                "signal": "Signal1"
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "Signal deleted successfully."
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It fetches the `assigned_resources` object by the provided signal name and deletes it.
        - On error, it returns a JSON response with an appropriate error message and status code.
    """
    if request.method == "DELETE":
        data = json.loads(request.body.decode('utf-8'))
        assigned_resources.objects.get(signal=data['signal']).delete()

    return JsonResponse({"success":True,"message":'signal deleted successfully'},safe=False) 

def update_interface_connector(request):
    """
    Update an interface-connector association based on the provided data.

    This view function handles the updating of an `interfaceConnector` object. 
    It processes the incoming JSON data to update the interface and connector 
    associations and returns a JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.

    Examples:
        Example JSON request body for updating an interface-connector association:
        
        .. code-block:: json

            {
                "interface_connector_id": 1,
                "interface_id": 2,
                "connector_id": 3
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "InterfaceConnector updated successfully."
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It fetches the `interfaceConnector` object by the provided ID and updates its attributes.
        - The function returns a success message on successful update.
        - On error, it returns a JSON response with an appropriate error message and status code.
    """
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        interface_connector_id = data.get('interface_connector_id')
        new_interface_id = data.get('interface_id')
        new_connector_id = data.get('connector_id')
        
        try:
            interface_connector = interfaceConnector.objects.get(id=interface_connector_id)
            interface_connector.interface_id = new_interface_id
            interface_connector.connector_id = new_connector_id
            interface_connector.save()
            return JsonResponse({"success": True, "message": "InterfaceConnector updated successfully."})
        except interfaceConnector.DoesNotExist:
            return JsonResponse({"success": False, "message": "InterfaceConnector not found."}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

def delete_interface_connector(request):
    """
    Delete an interface-connector association based on the provided data.

    This view function handles the deletion of an `interfaceConnector` object. 
    It processes the incoming JSON data to identify the interface-connector 
    association to delete and returns a JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.

    Examples:
        Example JSON request body for deleting an interface-connector association:
        
        .. code-block:: json

            {
                "interface_connector_id": 1
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "InterfaceConnector deleted successfully."
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It fetches the `interfaceConnector` object by the provided ID and deletes it.
        - The function returns a success message on successful deletion.
        - On error, it returns a JSON response with an appropriate error message and status code.
    """
    if request.method == "DELETE":
        data = json.loads(request.body.decode('utf-8'))
        interface_connector_id = data.get('interface_connector_id')
        
        try:
            interface_connector = interfaceConnector.objects.get(id=interface_connector_id)
            interface_connector.delete()
            return JsonResponse({"success": True, "message": "InterfaceConnector deleted successfully."})
        except interfaceConnector.DoesNotExist:
            return JsonResponse({"success": False, "message": "InterfaceConnector not found."}, status=404)
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)



# def associate_connecteur(request):
#     if request.method == "POST":
#         data = json.loads(request.body.decode('utf-8'))

#         # Retrieve the interface object from the database based on the received data
#         interface = interfaces.objects.get(interface=data['interface'])
#         # Create a new connecteur object with the specified dimensions, interface, and save it to the database
#         connecteur.objects.create(dimension_row=int(data['row']),dimension_column=int(data['column']),interface=interface)

#     return JsonResponse({"success":True,"message":'we associated an interface with a connecteur'},safe=False)    

def associate_connecteur(request):
    """
    Associate a connector (connecteur) with an interface based on the provided data.

    This view function handles the creation of a `connecteur` object and associates it 
    with an `interfaces` object. It processes the incoming JSON data to create the connector 
    and returns a JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.

    Examples:
        Example JSON request body for associating a connecteur:
        
        .. code-block:: json

            {
                "interface": "Interface1",
                "row": 10,
                "column": 5
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "Successfully associated an interface with a connecteur."
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It checks for the presence of required fields in the received data.
        - It retrieves the `interfaces` object by the provided interface name.
        - It creates a new `connecteur` object with the specified dimensions and associates it with the interface.
        - The function returns a success message on successful association.
        - On error, it returns a JSON response with an appropriate error message and status code.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode('utf-8'))

            # Check if the required fields are present in the received data
            if 'interface' not in data or 'row' not in data or 'column' not in data:
                return JsonResponse({"success": False, "message": "Missing required data fields."}, status=400)

            # Retrieve the interface object from the database based on the received data
            interface = interfaces.objects.get(interface=data['interface'])

            # Create a new connecteur object with the specified dimensions and interface, and save it to the database
            connecteur.objects.create(dimension_row=int(data['row']), dimension_column=int(data['column']), interface=interface)

            return JsonResponse({"success": True, "message": 'Successfully associated an interface with a connecteur'}, safe=False)
        except interfaces.DoesNotExist:
            return JsonResponse({"success": False, "message": "Interface not found."}, status=404)
        except Exception as e:
            # Log the error for debugging purposes
            print(e)
            return JsonResponse({"success": False, "message": "An error occurred while processing the request."}, status=500)

    return JsonResponse({"success": False, "message": "Invalid request method."}, status=405)

def delete_connecteur(request):
    """
    Delete a connecteur based on the provided data.

    This view function handles the deletion of a `connecteur` object. 
    It processes the incoming JSON data to identify the connecteur to delete and 
    returns a JSON response indicating success or failure.

    Args:
        request (HttpRequest): The HTTP request object containing the JSON data.

    Returns:
        JsonResponse: A JSON response indicating the success or failure of the operation.

    Examples:
        Example JSON request body for deleting a connecteur:
        
        .. code-block:: json

            {
                "connecteur": "Connecteur1"
            }

        Example JSON response on success:
        
        .. code-block:: json

            {
                "success": True,
                "message": "Connecteur deleted successfully."
            }

    Notes:
        - The function uses `json.loads` to parse the incoming JSON data.
        - It fetches the `connecteur` object by the provided connecteur name and deletes it.
        - The function returns a success message on successful deletion.
        - On error, it returns a JSON response with an appropriate error message and status code.
    """
    if request.method == "DELETE":
        data = json.loads(request.body.decode('utf-8'))
        connecteur.objects.get(connecteur=data['connecteur']).delete()

    return JsonResponse({"success":True,"message":'connecteur deleted successfully'},safe=False) 

@csrf_exempt
def add_signal(request):
    """
    Add a new signal to the database.

    This view function allows the addition of a new `Signal` object to the database.
    It expects a POST request with a JSON payload containing the signal name.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response indicating success or failure.

    Examples:
        Example JSON request:
        
        .. code-block:: json

            {
                "name": "NewSignal"
            }

    Notes:
        - The request must be a POST request.
        - The `csrf_exempt` decorator is used to disable CSRF protection for this view.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')

            if not name:
                return HttpResponseBadRequest("Signal name is required")

            signal = Signal(name=name)
            signal.save()
            return JsonResponse({'message': 'Signal added successfully'}, status=201)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")
    else:
        return HttpResponseBadRequest("Invalid request method")

@csrf_exempt
def update_signal(request, signal_id):
    """
    Update an existing signal in the database.

    This view function allows the update of an existing `Signal` object in the database.
    It expects a PUT request with a JSON payload containing the new signal name.

    Args:
        request (HttpRequest): The HTTP request object.
        signal_id (int): The ID of the signal to be updated.

    Returns:
        JsonResponse: A JSON response indicating success or failure.

    Examples:
        Example JSON request:
        
        .. code-block:: json

            {
                "name": "UpdatedSignalName"
            }

    Notes:
        - The request must be a PUT request.
        - The `csrf_exempt` decorator is used to disable CSRF protection for this view.
    """
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            name = data.get('name')

            if not name:
                return HttpResponseBadRequest("Signal name is required")

            signal = Signal.objects.get(id=signal_id)
            signal.name = name
            signal.save()
            return JsonResponse({'message': 'Signal updated successfully'})
        except Signal.DoesNotExist:
            return JsonResponse({'message': 'Signal not found'}, status=404)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")
    else:
        return HttpResponseBadRequest("Invalid request method")

@csrf_exempt
def delete_signal(request, signal_id):
    """
    Delete an existing signal from the database.

    This view function allows the deletion of an existing `Signal` object from the database.
    It expects a DELETE request.

    Args:
        request (HttpRequest): The HTTP request object.
        signal_id (int): The ID of the signal to be deleted.

    Returns:
        JsonResponse: A JSON response indicating success or failure.

    Notes:
        - The request must be a DELETE request.
        - The `csrf_exempt` decorator is used to disable CSRF protection for this view.
    """
    if request.method == 'DELETE':
        try:
            signal = Signal.objects.get(id=signal_id)
            signal.delete()
            return JsonResponse({'message': 'Signal deleted successfully'})
        except Signal.DoesNotExist:
            return JsonResponse({'message': 'Signal not found'}, status=404)
    else:
        return HttpResponseBadRequest("Invalid request method")