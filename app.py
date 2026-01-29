"""
Flask API for Designation Management System
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime, date
import json
import os
from typing import List

from models import Person, DesignationType, AVAILABLE_DESIGNATIONS
from designation_manager import DesignationManager

app = Flask(__name__, static_folder='static')
CORS(app)

# Initialize the designation manager
manager = DesignationManager()

# Data persistence file
DATA_DIR = 'data'
PEOPLE_FILE = os.path.join(DATA_DIR, 'people.json')
SCHEDULES_FILE = os.path.join(DATA_DIR, 'schedules.json')


def ensure_data_dir():
    """Ensure the data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_data():
    """Load people and schedules from files"""
    ensure_data_dir()
    
    # Load people
    if os.path.exists(PEOPLE_FILE):
        try:
            with open(PEOPLE_FILE, 'r', encoding='utf-8') as f:
                people_data = json.load(f)
                for person_dict in people_data:
                    person = Person.from_dict(person_dict)
                    try:
                        manager.add_person(person)
                    except ValueError:
                        pass  # Person already exists
        except (json.JSONDecodeError, KeyError) as e:
            print(f"ERROR: Failed to load people data - file may be corrupted: {e}")
            print("Starting with empty people list")
        except Exception as e:
            print(f"ERROR: Unexpected error loading people: {e}")
            print("Starting with empty people list")
    
    # Load schedules
    if os.path.exists(SCHEDULES_FILE):
        try:
            with open(SCHEDULES_FILE, 'r', encoding='utf-8') as f:
                schedules_data = json.load(f)
                from models import MonthlySchedule
                for schedule_dict in schedules_data:
                    schedule = MonthlySchedule.from_dict(schedule_dict)
                    manager.schedules[(schedule.year, schedule.month)] = schedule
        except (json.JSONDecodeError, KeyError) as e:
            print(f"ERROR: Failed to load schedules data - file may be corrupted: {e}")
            print("Starting with empty schedules")
        except Exception as e:
            print(f"ERROR: Unexpected error loading schedules: {e}")
            print("Starting with empty schedules")


def save_data():
    """Save people and schedules to files"""
    try:
        ensure_data_dir()
        
        # Save people
        people_data = [p.to_dict() for p in manager.people]
        with open(PEOPLE_FILE, 'w', encoding='utf-8') as f:
            json.dump(people_data, f, indent=2, ensure_ascii=False)
        
        # Save schedules
        schedules_data = [s.to_dict() for s in manager.schedules.values()]
        with open(SCHEDULES_FILE, 'w', encoding='utf-8') as f:
            json.dump(schedules_data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving data: {e}")
        raise


@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('static', 'index.html')


@app.route('/api/people', methods=['GET'])
def get_people():
    """Get all people"""
    return jsonify([p.to_dict() for p in manager.people])


@app.route('/api/people', methods=['POST'])
def add_person():
    """Add a new person"""
    data = request.json
    
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    # Validate name
    name = data['name'].strip()
    if not name or len(name) < 1:
        return jsonify({'error': 'Name cannot be empty'}), 400
    if len(name) > 100:
        return jsonify({'error': 'Name is too long (max 100 characters)'}), 400
    
    # Generate new ID
    max_id = max([p.id for p in manager.people], default=0)
    new_id = max_id + 1
    
    person = Person(
        id=new_id,
        name=name,
        available=data.get('available', True)
    )
    
    try:
        manager.add_person(person)
        save_data()
        return jsonify(person.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/people/<int:person_id>', methods=['PUT'])
def update_person(person_id):
    """Update a person"""
    person = manager.get_person(person_id)
    if not person:
        return jsonify({'error': 'Person not found'}), 404
    
    data = request.json
    if 'name' in data:
        person.name = data['name']
    if 'available' in data:
        person.available = data['available']
    
    save_data()
    return jsonify(person.to_dict())


@app.route('/api/people/<int:person_id>', methods=['DELETE'])
def delete_person(person_id):
    """Delete a person"""
    person = manager.get_person(person_id)
    if not person:
        return jsonify({'error': 'Person not found'}), 404
    
    manager.remove_person(person_id)
    save_data()
    return jsonify({'message': 'Person deleted'}), 200


@app.route('/api/designations', methods=['GET'])
def get_designations():
    """Get all available designation types"""
    return jsonify([d.to_dict() for d in AVAILABLE_DESIGNATIONS])


@app.route('/api/schedules/<int:year>/<int:month>', methods=['GET'])
def get_schedule(year, month):
    """Get a specific monthly schedule"""
    schedule = manager.get_schedule(year, month)
    if not schedule:
        return jsonify({'error': 'Schedule not found'}), 404
    
    summary = manager.get_schedule_summary(schedule)
    return jsonify(summary)


@app.route('/api/schedules/<int:year>/<int:month>/generate', methods=['POST'])
def generate_schedule(year, month):
    """Generate a monthly schedule"""
    data = request.json
    
    if not data or 'dates' not in data:
        return jsonify({'error': 'Meeting dates are required'}), 400
    
    try:
        # Parse dates
        meeting_dates = []
        for date_str in data['dates']:
            meeting_date = datetime.fromisoformat(date_str).date()
            
            # Validate that date belongs to the specified month and year
            if meeting_date.year != year or meeting_date.month != month:
                return jsonify({
                    'error': f'Date {date_str} does not belong to {month}/{year}'
                }), 400
            
            meeting_dates.append(meeting_date)
        
        # Generate schedule
        schedule = manager.generate_monthly_schedule(year, month, meeting_dates)
        save_data()
        
        summary = manager.get_schedule_summary(schedule)
        return jsonify(summary), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Error generating schedule: {str(e)}'}), 500


@app.route('/api/schedules/<int:year>/<int:month>', methods=['DELETE'])
def delete_schedule(year, month):
    """Delete a monthly schedule"""
    if not manager.get_schedule(year, month):
        return jsonify({'error': 'Schedule not found'}), 404
    
    manager.clear_schedule(year, month)
    save_data()
    return jsonify({'message': 'Schedule deleted'}), 200


@app.route('/api/schedules', methods=['GET'])
def list_schedules():
    """List all available schedules"""
    schedules = []
    for (year, month), schedule in manager.schedules.items():
        schedules.append({
            'year': year,
            'month': month,
            'assignment_count': len(schedule.assignments)
        })
    return jsonify(schedules)


if __name__ == '__main__':
    # Load existing data
    load_data()
    
    # Run the Flask app
    # Note: For production, use a WSGI server like gunicorn
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
