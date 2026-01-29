"""
Data models for the Designation Management System
"""
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import date
from enum import Enum


class DesignationType(Enum):
    """Types of designations available"""
    PRESIDENCIA = "Presidência"
    LEITURA = "Leitura"
    ORACAO_FINAL = "Oração Final"
    AUDIO_VIDEO = "Áudio & Vídeo"
    PALCO = "Palco"
    INDICADOR = "Indicador"
    MICROFONE_VOLANTE = "Microfone Volante"


@dataclass
class Person:
    """Represents a person who can receive designations"""
    id: int
    name: str
    available: bool = True
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'available': self.available
        }
    
    @staticmethod
    def from_dict(data):
        return Person(
            id=data['id'],
            name=data['name'],
            available=data.get('available', True)
        )


@dataclass
class Designation:
    """Represents a designation type and its requirements"""
    type: DesignationType
    required_people: int
    
    def to_dict(self):
        return {
            'type': self.type.name,
            'type_display': self.type.value,
            'required_people': self.required_people
        }


@dataclass
class Assignment:
    """Represents an assignment of a person to a designation on a specific date"""
    date: date
    designation: DesignationType
    person_id: int
    
    def to_dict(self):
        return {
            'date': self.date.isoformat(),
            'designation': self.designation.name,
            'designation_display': self.designation.value,
            'person_id': self.person_id
        }
    
    @staticmethod
    def from_dict(data):
        return Assignment(
            date=date.fromisoformat(data['date']),
            designation=DesignationType[data['designation']],
            person_id=data['person_id']
        )


@dataclass
class MonthlySchedule:
    """Represents a complete monthly schedule with all assignments"""
    year: int
    month: int
    assignments: List[Assignment] = field(default_factory=list)
    
    def add_assignment(self, assignment: Assignment):
        """Add an assignment to the schedule"""
        self.assignments.append(assignment)
    
    def get_assignments_for_date(self, target_date: date) -> List[Assignment]:
        """Get all assignments for a specific date"""
        return [a for a in self.assignments if a.date == target_date]
    
    def get_person_assignments_for_date(self, person_id: int, target_date: date) -> List[Assignment]:
        """Get all assignments for a specific person on a specific date"""
        return [a for a in self.assignments 
                if a.person_id == person_id and a.date == target_date]
    
    def count_person_assignments_for_date(self, person_id: int, target_date: date) -> int:
        """Count how many designations a person has on a specific date"""
        return len(self.get_person_assignments_for_date(person_id, target_date))
    
    def to_dict(self):
        return {
            'year': self.year,
            'month': self.month,
            'assignments': [a.to_dict() for a in self.assignments]
        }
    
    @staticmethod
    def from_dict(data):
        schedule = MonthlySchedule(
            year=data['year'],
            month=data['month']
        )
        for assignment_data in data.get('assignments', []):
            schedule.add_assignment(Assignment.from_dict(assignment_data))
        return schedule


# Define all available designations with their requirements
AVAILABLE_DESIGNATIONS = [
    Designation(DesignationType.PRESIDENCIA, 1),
    Designation(DesignationType.LEITURA, 1),
    Designation(DesignationType.ORACAO_FINAL, 1),
    Designation(DesignationType.AUDIO_VIDEO, 1),
    Designation(DesignationType.PALCO, 1),
    Designation(DesignationType.INDICADOR, 2),
    Designation(DesignationType.MICROFONE_VOLANTE, 2),
]
