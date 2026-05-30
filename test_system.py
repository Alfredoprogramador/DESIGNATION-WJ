"""
Test script to validate the designation management system
"""
from datetime import date, timedelta
from models import Person, DesignationType
from designation_manager import DesignationManager


def test_basic_functionality():
    """Test basic functionality of the designation manager"""
    print("🧪 Testing Designation Management System\n")
    
    # Create manager
    manager = DesignationManager()
    print("✓ Manager created")
    
    # Add people
    people = [
        Person(1, "João Silva"),
        Person(2, "Maria Santos"),
        Person(3, "Pedro Oliveira"),
        Person(4, "Ana Costa"),
        Person(5, "Carlos Souza"),
        Person(6, "Juliana Lima"),
        Person(7, "Roberto Alves"),
        Person(8, "Fernanda Rocha"),
        Person(9, "Lucas Pereira"),
        Person(10, "Patrícia Martins"),
    ]
    
    for person in people:
        manager.add_person(person)
    print(f"✓ Added {len(people)} people")
    
    # Test getting people
    assert len(manager.people) == 10
    assert len(manager.get_available_people()) == 10
    print("✓ All people are available")
    
    # Test making someone unavailable
    people[0].available = False
    assert len(manager.get_available_people()) == 9
    people[0].available = True
    print("✓ Availability toggle works")
    
    # Generate a schedule for January 2026
    year = 2026
    month = 1
    
    # Create meeting dates (4 Sundays in January)
    meeting_dates = [
        date(2026, 1, 4),   # First Sunday
        date(2026, 1, 11),  # Second Sunday
        date(2026, 1, 18),  # Third Sunday
        date(2026, 1, 25),  # Fourth Sunday
    ]
    
    print(f"\n📅 Generating schedule for {month}/{year}")
    print(f"   Meeting dates: {[d.strftime('%d/%m/%Y') for d in meeting_dates]}")
    
    try:
        schedule = manager.generate_monthly_schedule(year, month, meeting_dates)
        print(f"✓ Schedule generated with {len(schedule.assignments)} assignments")
        
        # Verify constraint: no person has more than 2 designations per day
        for meeting_date in meeting_dates:
            for person in people:
                count = schedule.count_person_assignments_for_date(person.id, meeting_date)
                assert count <= 2, f"Person {person.name} has {count} designations on {meeting_date}"
        print("✓ Constraint validated: No person has more than 2 designations per day")
        
        # Display the schedule
        print("\n" + "="*70)
        print("📋 ESCALA GERADA")
        print("="*70)
        
        summary = manager.get_schedule_summary(schedule)
        for date_info in summary['dates']:
            date_obj = date.fromisoformat(date_info['date'])
            print(f"\n📅 {date_obj.strftime('%d/%m/%Y - %A')}")
            print("-" * 70)
            
            for designation, people_names in date_info['assignments'].items():
                print(f"  {designation:25} : {', '.join(people_names)}")
        
        print("\n" + "="*70)
        
        # Count assignments per person
        print("\n📊 DISTRIBUIÇÃO DE DESIGNAÇÕES")
        print("-" * 70)
        assignment_counts = {}
        for assignment in schedule.assignments:
            person = manager.get_person(assignment.person_id)
            if person:
                assignment_counts[person.name] = assignment_counts.get(person.name, 0) + 1
        
        for name in sorted(assignment_counts.keys()):
            count = assignment_counts[name]
            bar = "█" * count
            print(f"  {name:20} : {bar} ({count})")
        
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error generating schedule: {e}")
        return False


if __name__ == "__main__":
    success = test_basic_functionality()
    exit(0 if success else 1)
