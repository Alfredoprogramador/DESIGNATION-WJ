"""
Designation Manager - Core logic for managing and assigning designations
"""
from typing import List, Dict, Optional
from datetime import date, timedelta
import random
from models import (
    Person, Designation, Assignment, MonthlySchedule,
    DesignationType, AVAILABLE_DESIGNATIONS
)


class DesignationManager:
    """Manages people and their designations"""
    
    MAX_DESIGNATIONS_PER_DAY = 2
    
    def __init__(self):
        self.people: List[Person] = []
        self.schedules: Dict[tuple, MonthlySchedule] = {}  # Key: (year, month)
    
    def add_person(self, person: Person):
        """Add a person to the system"""
        # Check if person with same ID already exists
        if any(p.id == person.id for p in self.people):
            raise ValueError(f"Person with ID {person.id} already exists")
        self.people.append(person)
    
    def remove_person(self, person_id: int):
        """Remove a person from the system"""
        self.people = [p for p in self.people if p.id != person_id]
    
    def get_person(self, person_id: int) -> Optional[Person]:
        """Get a person by ID"""
        for person in self.people:
            if person.id == person_id:
                return person
        return None
    
    def get_available_people(self) -> List[Person]:
        """Get all available people"""
        return [p for p in self.people if p.available]
    
    def can_assign_designation(self, person_id: int, target_date: date, 
                               schedule: MonthlySchedule) -> bool:
        """
        Check if a person can be assigned a designation on a specific date.
        Returns True if the person has less than MAX_DESIGNATIONS_PER_DAY on that date.
        """
        count = schedule.count_person_assignments_for_date(person_id, target_date)
        return count < self.MAX_DESIGNATIONS_PER_DAY
    
    def assign_designation(self, person_id: int, target_date: date, 
                          designation: DesignationType,
                          schedule: MonthlySchedule) -> bool:
        """
        Assign a designation to a person for a specific date.
        Returns True if successful, False otherwise.
        """
        # Check if person exists
        person = self.get_person(person_id)
        if not person:
            raise ValueError(f"Person with ID {person_id} not found")
        
        # Check if person is available
        if not person.available:
            raise ValueError(f"Person {person.name} is not available")
        
        # Check constraint: max 2 designations per day
        if not self.can_assign_designation(person_id, target_date, schedule):
            raise ValueError(
                f"Person {person.name} already has {self.MAX_DESIGNATIONS_PER_DAY} "
                f"designations on {target_date}"
            )
        
        # Create and add the assignment
        assignment = Assignment(
            date=target_date,
            designation=designation,
            person_id=person_id
        )
        schedule.add_assignment(assignment)
        return True
    
    def generate_monthly_schedule(self, year: int, month: int, 
                                 meeting_dates: List[date]) -> MonthlySchedule:
        """
        Generate a complete monthly schedule for all meeting dates.
        Attempts to distribute designations fairly among available people.
        """
        schedule = MonthlySchedule(year=year, month=month)
        available_people = self.get_available_people()
        
        if len(available_people) < 3:
            raise ValueError("Need at least 3 people to generate a schedule")
        
        # Track assignments per person to distribute fairly
        assignment_counts = {person.id: 0 for person in available_people}
        
        for meeting_date in meeting_dates:
            # Shuffle people for randomness in assignment
            people_pool = available_people.copy()
            random.shuffle(people_pool)
            
            # Assign each designation for this date
            for designation_def in AVAILABLE_DESIGNATIONS:
                assigned_count = 0
                
                # Try to assign required number of people
                for person in people_pool:
                    if assigned_count >= designation_def.required_people:
                        break
                    
                    # Check if person can be assigned
                    if self.can_assign_designation(person.id, meeting_date, schedule):
                        try:
                            self.assign_designation(
                                person.id, meeting_date,
                                designation_def.type, schedule
                            )
                            assignment_counts[person.id] += 1
                            assigned_count += 1
                        except ValueError:
                            # Can't assign, try next person
                            continue
                
                # If we couldn't assign enough people, that's a problem
                if assigned_count < designation_def.required_people:
                    raise ValueError(
                        f"Could not assign enough people for {designation_def.type.value} "
                        f"on {meeting_date}. Needed {designation_def.required_people}, "
                        f"got {assigned_count}"
                    )
        
        # Store the schedule
        self.schedules[(year, month)] = schedule
        return schedule
    
    def get_schedule(self, year: int, month: int) -> Optional[MonthlySchedule]:
        """Get a monthly schedule if it exists"""
        return self.schedules.get((year, month))
    
    def clear_schedule(self, year: int, month: int):
        """Clear a monthly schedule"""
        if (year, month) in self.schedules:
            del self.schedules[(year, month)]
    
    def get_schedule_summary(self, schedule: MonthlySchedule) -> Dict:
        """
        Generate a summary of a schedule showing assignments organized by date.
        """
        dates = sorted(set(a.date for a in schedule.assignments))
        summary = []
        
        for target_date in dates:
            date_assignments = schedule.get_assignments_for_date(target_date)
            
            # Group by designation type
            by_designation = {}
            for assignment in date_assignments:
                designation_name = assignment.designation.value
                if designation_name not in by_designation:
                    by_designation[designation_name] = []
                
                person = self.get_person(assignment.person_id)
                if person:
                    by_designation[designation_name].append(person.name)
            
            summary.append({
                'date': target_date.isoformat(),
                'assignments': by_designation
            })
        
        return {
            'year': schedule.year,
            'month': schedule.month,
            'dates': summary
        }
