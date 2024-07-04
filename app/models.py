from django.db import models
import json
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
# les finctions __str__ servent à donner un nom à l'objet, au lieu d'avoir comme nom par défaut 
# < Objet(primary_key "soit id soit une clè primaire défini") > au lieu d'avoir cette représentation
# par défaut on va avoir le texte défini par __str__ entre <>

class Folder(models.Model):
    folder_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.folder_name}"

class File(models.Model):
    file_name = models.CharField(max_length=255)
    folder_name = models.ForeignKey(Folder, related_name="files", on_delete=models.CASCADE)
    data = models.BinaryField()  

    def __str__(self):
        return f"Dossier {self.folder_name.folder_name} : fichier {self.file_name}"
    
class io_type(models.Model):
    io_type_name = models.CharField(primary_key=True, max_length=255)
    io_type_symbol = models.CharField(null=True, max_length=255)

class resources_categories(models.Model):
    category = models.CharField(primary_key=True, max_length=255)
    count = models.IntegerField(null=True, default=0) 
    io_type = models.ManyToManyField(io_type, related_name='resources_categories')

    def __str__(self):
        return f"Category : {self.category}"

class Signal(models.Model):
    name = models.CharField(max_length=255, unique=True, default='signal')

    def __str__(self):
        return self.name
    
class assigned_resources(models.Model):
    signal = models.ForeignKey(Signal, on_delete=models.CASCADE, default=1)
    board_internal_mapping = models.CharField(max_length=255)
    #commentaire = models.TextField(blank=True)
    io_type = models.ForeignKey(io_type, null=True, on_delete=models.SET_NULL)
    #io_index = models.CharField(max_length=255)
    category = models.ForeignKey(resources_categories, on_delete=models.CASCADE, default='default') #resource_name

    def __str__(self):
        return f"signal : {self.signal.name} de la catégorie {self.category.category}"

class resource_name(models.Model):
    name = models.TextField(primary_key=True)  

class boards(models.Model):
    board = models.TextField(primary_key=True)
    
    def __str__(self):
        return f"board {self.board}"

class interfaces(models.Model):
    interface = models.TextField(primary_key=True)
    board1 = models.ForeignKey(boards, related_name='board1_interfaces', on_delete=models.CASCADE)
    board2 = models.ForeignKey(boards, related_name='board2_interfaces', on_delete=models.CASCADE)

    def __str__(self):
        return f"interface {self.interface}"

class connecteur(models.Model):
    dimension_row = models.IntegerField()  
    dimension_column = models.IntegerField()
    interface = models.ForeignKey(interfaces, on_delete=models.CASCADE, related_name="connected")

class connector(models.Model):
    name = models.CharField(max_length=100, unique=True, default='defaultName')
    row_dim = models.IntegerField()
    column_dim = models.IntegerField()

    def __str__(self):
        return f"{self.name} ({self.row_dim}x{self.column_dim})"
    
class interfaceConnector(models.Model):
    interface = models.ForeignKey(interfaces, on_delete=models.CASCADE, related_name='connectors')
    connecteur = models.ForeignKey(connector, on_delete=models.CASCADE, related_name='interfaces')
    matrix = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.interface} connected to {self.connecteur}"

    def save(self, *args, **kwargs):
        # Initialize the matrix if it's empty
        if not self.matrix:
            self.matrix = json.dumps([["" for _ in range(self.connecteur.column_dim)] for _ in range(self.connecteur.row_dim)])
        super().save(*args, **kwargs)

    def get_matrix(self):
        return json.loads(self.matrix)

    def set_matrix(self, matrix):
        self.matrix = json.dumps(matrix)
        self.save()

    
class association(models.Model):
    resource = models.ForeignKey(resource_name, on_delete=models.CASCADE, related_name="resource")
    interface = models.ForeignKey(interfaces, on_delete=models.CASCADE, related_name="interfaces")
    nombre_resource = models.IntegerField()

class IO_list(models.Model):
    resource_name = models.IntegerField()
    signal = models.ForeignKey(Signal, on_delete=models.CASCADE)
    nature = models.CharField(max_length=255)
    from_to = models.CharField(max_length=255)
    source_destination_board = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    connector = models.CharField(max_length=255)
    interface_resource = models.ForeignKey(association, related_name="IO_list", on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Signal : {self.signal.name} de l'interface {self.interface_resource.interface.interface}"

class contacts(models.Model):
    connecteur = models.ForeignKey(connecteur, related_name="contacts", on_delete=models.CASCADE)
    signal = models.ForeignKey(Signal, on_delete=models.CASCADE, default=1)
    num_row = models.IntegerField()
    num_column = models.IntegerField()

    def __str__(self):
        return f"le contact {self.signal.name} dans {self.connecteur.interface.interface}"

class link(models.Model):
    first_interface = models.CharField(max_length=255)
    second_interface = models.CharField(max_length=255)
    nom_link = models.CharField(max_length=255, primary_key=True)

class wirings(models.Model):
    link_type = models.ForeignKey(link, related_name="wirings", on_delete=models.CASCADE)
    first_signal = models.TextField(blank=True)
    second_signal = models.TextField(blank=True)

class modele_io_mapping(models.Model):
    modele_name = models.CharField(primary_key=True, max_length=255)
    resources = models.ManyToManyField(resources_categories)
    iotypes = models.ManyToManyField(io_type)
    resource_names = models.ManyToManyField(resource_name)
    interfaces = models.ManyToManyField(interfaces)
    links = models.ManyToManyField(link)

class IO_list(models.Model):
    assigned_resource = models.ForeignKey(assigned_resources, null=True, on_delete=models.CASCADE)
    nature = models.CharField(max_length=255)
    from_to = models.CharField(max_length=255)
    source_destination_board = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    connector = models.CharField(max_length=255)

    def __str__(self):
        return f"Signal: {self.assigned_resource.signal.name} from Category: {self.assigned_resource.category.category}"
