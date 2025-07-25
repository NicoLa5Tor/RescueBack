from datetime import datetime
from dataclasses import dataclass
from typing import Optional

@dataclass
class Contact:
    """Modelo para las consultas de contacto"""
    firstName: str
    lastName: str
    email: str
    company: str
    phone: Optional[str]
    projectType: str
    message: Optional[str]
    privacy: bool
    created_at: datetime
    email_id: Optional[str] = None
    status: str = "pending"  # pending, sent, failed
    
    def to_dict(self):
        """Convierte el objeto a diccionario para MongoDB"""
        return {
            'firstName': self.firstName,
            'lastName': self.lastName,
            'email': self.email,
            'company': self.company,
            'phone': self.phone,
            'projectType': self.projectType,
            'message': self.message,
            'privacy': self.privacy,
            'created_at': self.created_at,
            'email_id': self.email_id,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Crea un objeto Contact desde un diccionario"""
        return cls(
            firstName=data.get('firstName'),
            lastName=data.get('lastName'),
            email=data.get('email'),
            company=data.get('company'),
            phone=data.get('phone'),
            projectType=data.get('projectType'),
            message=data.get('message'),
            privacy=data.get('privacy'),
            created_at=data.get('created_at'),
            email_id=data.get('email_id'),
            status=data.get('status', 'pending')
        )
