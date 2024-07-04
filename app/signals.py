from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver

def create_assigned_resources(sender, instance, created, **kwargs):
    """
    Signal receiver that creates or updates assigned resources when a resources_categories instance is saved.

    This function is triggered after a resources_categories instance is saved. It handles 
    both the creation of new assigned resources when a new category is created and the 
    update of existing assigned resources when a category's count is modified.

    Args:
        sender (Model): The model class that sent the signal.
        instance (resources_categories): The instance of the model that was saved.
        created (bool): A boolean indicating whether a new record was created.
        **kwargs: Additional keyword arguments.

    Examples:
        When a new resources_categories instance is created:
        
        .. code-block:: python

            category = resources_categories.objects.create(category='NewCategory', count=5)
            # This will automatically create 5 assigned_resources instances for the new category.

        When an existing resources_categories instance is updated:
        
        .. code-block:: python

            category = resources_categories.objects.get(category='NewCategory')
            category.count = 10
            category.save()
            # This will automatically update the assigned_resources instances to match the new count.

    Notes:
        - The `create_assigned_resources` function uses Django's `post_save` signal to automatically 
          manage the creation and updating of `assigned_resources` instances. This ensures that the 
          number of `assigned_resources` matches the `count` attribute of the `resources_categories` 
          instance.
        - If the `resources_categories` instance is newly created, the function creates the specified 
          number of `assigned_resources` instances.
        - If the `resources_categories` instance is updated, the function checks whether the number of 
          existing `assigned_resources` instances matches the `count` attribute. If not, it deletes the 
          existing instances and creates new ones to match the updated count.
        - This automation helps maintain data consistency and integrity by ensuring that the number of 
          `assigned_resources` is always in sync with the `count` attribute of the `resources_categories` 
          instance.

    """
    if created:
        # Create new assigned resources if the instance is newly created
        assigned_resources.objects.bulk_create([
            assigned_resources(category=instance)
            for _ in range(instance.count)
        ])
    else:
        # If the instance is updated and not created, handle changes accordingly
        existing_signals = assigned_resources.objects.filter(category=instance)
        if existing_signals.count() != instance.count:
            existing_signals.delete()  # Clear out the existing signals
            assigned_resources.objects.bulk_create([
                assigned_resources(category=instance)
                for _ in range(instance.count)
            ])
