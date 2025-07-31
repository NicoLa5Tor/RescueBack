from typing import List, Optional
from bson.objectid import ObjectId
from models.contact import Contact
from database import Database

class ContactRepository:
    """Repository para manejar operaciones CRUD de contactos"""
    
    def __init__(self):
        self.db = Database()
        database = self.db.get_database()
        self.collection = database['contacts']
    
    def create_contact(self, contact: Contact) -> str:
        """
        Crear un nuevo contacto
        Returns: str - ID del contacto creado
        """
        try:
            contact_dict = contact.to_dict()
            result = self.collection.insert_one(contact_dict)
            return str(result.inserted_id)
        except Exception as e:
            # print(f"Error creating contact: {e}")
            raise Exception(f"No se pudo crear el contacto: {str(e)}")
    
    def get_contact_by_id(self, contact_id: str) -> Optional[Contact]:
        """
        Obtener contacto por ID
        """
        try:
            contact_data = self.collection.find_one({'_id': ObjectId(contact_id)})
            if contact_data:
                contact_data['id'] = str(contact_data['_id'])
                return Contact.from_dict(contact_data)
            return None
        except Exception as e:
            # print(f"Error getting contact by ID: {e}")
            return None
    
    def get_all_contacts(self, limit: int = 100, skip: int = 0) -> List[Contact]:
        """
        Obtener todos los contactos con paginación
        """
        try:
            contacts_data = self.collection.find().sort('created_at', -1).limit(limit).skip(skip)
            contacts = []
            for contact_data in contacts_data:
                contact_data['id'] = str(contact_data['_id'])
                contacts.append(Contact.from_dict(contact_data))
            return contacts
        except Exception as e:
            # print(f"Error getting all contacts: {e}")
            return []
    
    def update_contact_status(self, contact_id: str, status: str, email_id: str = None) -> bool:
        """
        Actualizar el status de un contacto
        """
        try:
            update_data = {'status': status}
            if email_id:
                update_data['email_id'] = email_id
            
            result = self.collection.update_one(
                {'_id': ObjectId(contact_id)},
                {'$set': update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            # print(f"Error updating contact status: {e}")
            return False
    
    def get_contacts_by_status(self, status: str) -> List[Contact]:
        """
        Obtener contactos por status
        """
        try:
            contacts_data = self.collection.find({'status': status}).sort('created_at', -1)
            contacts = []
            for contact_data in contacts_data:
                contact_data['id'] = str(contact_data['_id'])
                contacts.append(Contact.from_dict(contact_data))
            return contacts
        except Exception as e:
            # print(f"Error getting contacts by status: {e}")
            return []
    
    def count_contacts(self) -> int:
        """
        Contar total de contactos
        """
        try:
            return self.collection.count_documents({})
        except Exception as e:
            # print(f"Error counting contacts: {e}")
            return 0
