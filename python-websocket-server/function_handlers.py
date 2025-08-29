"""
Function handlers for OpenAI Realtime API function calling.

This module defines the available functions that can be called by the AI assistant.
Converted from TypeScript functionHandlers.ts to Python.

Each function handler includes:
1. Schema definition (for OpenAI API)
2. Implementation function (async Python function)
"""

import json
import httpx
from typing import Dict, Any, List
from models import FunctionSchema, PatientCreate, AppointmentCreate, EmergencyCreate
from database import db_manager, create_emergency_from_call

from dotenv import load_dotenv
import os
from datetime import datetime, date

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

async def get_weather_from_coords(latitude: float, longitude: float) -> str:
    """
    Get current weather data from coordinates using Open-Meteo API.
    
    Converted from TypeScript fetch-based implementation to Python httpx.
    
    Args:
        latitude: Geographic latitude
        longitude: Geographic longitude
        
    Returns:
        JSON string containing weather data
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        f"&current=temperature_2m,wind_speed_10m"
        f"&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
        current_temp = data.get("current", {}).get("temperature_2m")
        return json.dumps({"temp": current_temp})
        
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch weather: {str(e)}"})


async def get_patient_details(patient_name: str) -> str:
    """
    Get patient details by name for the AI voice agent.
    
    Args:
        patient_name: Name of the patient to look up
        
    Returns:
        JSON string containing patient information or error message
    """
    try:
        # Search for patients by name
        patients = await db_manager.search_patients(
            PatientSearchQuery(name=patient_name, limit=5)
        )
        
        if not patients:
            return json.dumps({
                "error": f"No patient found with name '{patient_name}'",
                "suggestion": "Please verify the patient name or create a new patient record"
            })
        
        # If multiple patients found, return the first match with a note
        patient = patients[0]
        result = {
            "patient_id": patient.id,
            "name": patient.name,
            "phone": patient.phone,
            "email": patient.email,
            "date_of_birth": patient.date_of_birth,
            "language_preference": patient.preferences.language,
            "last_visit": patient.medical_history.last_visit,
            "allergies": patient.medical_history.allergies,
            "conditions": patient.medical_history.conditions,
            "emergency_contact": {
                "name": patient.emergency_contact.name,
                "phone": patient.emergency_contact.phone,
                "relationship": patient.emergency_contact.relationship
            }
        }
        
        if len(patients) > 1:
            result["note"] = f"Found {len(patients)} patients with similar names. Showing details for {patient.name}."
        
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to retrieve patient details: {str(e)}"
        })


async def schedule_appointment(patient_name: str, appointment_type: str, date: str, time: str, priority: str = "routine") -> str:
    """
    Schedule a new appointment for a patient.
    
    Args:
        patient_name: Name of the patient
        appointment_type: Type of appointment (e.g., "Emergency Consultation", "Routine Cleaning")
        date: Appointment date in YYYY-MM-DD format
        time: Appointment time (e.g., "2:30 PM")
        priority: Priority level (routine, treatment, emergency)
        
    Returns:
        JSON string with appointment confirmation or error message
    """
    try:
        # Find patient by name
        patients = await db_manager.search_patients(
            PatientSearchQuery(name=patient_name, limit=1)
        )
        
        if not patients:
            return json.dumps({
                "error": f"Patient '{patient_name}' not found",
                "suggestion": "Please verify the patient name or create a new patient record first"
            })
        
        patient = patients[0]
        
        # Determine duration based on appointment type
        duration_map = {
            "emergency consultation": 60,
            "routine cleaning": 45,
            "root canal": 90,
            "check-up": 30,
            "consultation": 45,
            "filling": 60,
            "extraction": 45
        }
        duration = duration_map.get(appointment_type.lower(), 45)
        
        # Create appointment
        appointment_data = AppointmentCreate(
            patient_name=patient.name,
            patient_id=patient.id,
            type=appointment_type,
            date=date,
            time=time,
            duration=duration,
            priority=priority,
            booked_via="voice_agent"
        )
        
        appointment = await db_manager.create_appointment(appointment_data)
        
        return json.dumps({
            "success": True,
            "appointment_id": appointment.id,
            "patient_name": appointment.patient_name,
            "type": appointment.type,
            "date": appointment.date,
            "time": appointment.time,
            "duration": f"{appointment.duration} minutes",
            "priority": appointment.priority,
            "status": appointment.status,
            "confirmation": f"Appointment scheduled for {patient.name} on {date} at {time} for {appointment_type}"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to schedule appointment: {str(e)}"
        })


async def get_appointments_for_date(date: str) -> str:
    """
    Get all appointments for a specific date.
    
    Args:
        date: Date in YYYY-MM-DD format
        
    Returns:
        JSON string with list of appointments for the date
    """
    try:
        appointments = await db_manager.get_appointments_by_date(date)
        
        if not appointments:
            return json.dumps({
                "date": date,
                "appointments": [],
                "message": f"No appointments scheduled for {date}"
            })
        
        appointment_list = []
        for apt in appointments:
            appointment_list.append({
                "id": apt.id,
                "patient_name": apt.patient_name,
                "type": apt.type,
                "time": apt.time,
                "duration": f"{apt.duration} minutes",
                "status": apt.status,
                "priority": apt.priority
            })
        
        return json.dumps({
            "date": date,
            "total_appointments": len(appointments),
            "appointments": appointment_list
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to retrieve appointments: {str(e)}"
        })


async def record_emergency_case(patient_name: str, phone: str, symptoms: str, pain_level: int, duration: str) -> str:
    """
    Record a new emergency case from a voice call.
    
    Args:
        patient_name: Name of the patient
        phone: Patient's phone number
        symptoms: Description of symptoms
        pain_level: Pain level from 1-10
        duration: How long symptoms have persisted
        
    Returns:
        JSON string with emergency case details and next actions
    """
    try:
        # Create emergency case
        emergency = await create_emergency_from_call(
            patient_name=patient_name,
            phone=phone,
            symptoms=symptoms,
            pain_level=pain_level,
            duration=duration
        )
        
        # Determine if immediate escalation is needed
        escalation_needed = pain_level >= 8 or "trauma" in symptoms.lower() or "accident" in symptoms.lower()
        
        result = {
            "emergency_id": emergency.id,
            "patient_name": emergency.patient_name,
            "priority": emergency.priority,
            "ai_assessment": emergency.ai_assessment,
            "next_action": emergency.next_action,
            "escalation_needed": escalation_needed,
            "status": emergency.status
        }
        
        if escalation_needed:
            result["urgent_message"] = "This case requires immediate attention. Please escalate to emergency dental services."
            result["emergency_contacts"] = {
                "dr_estrabillo": "(555) 123-4567",
                "emergency_line": "(555) 911-DENT",
                "hospital_referral": "(555) 456-7890"
            }
        
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to record emergency case: {str(e)}"
        })


async def create_patient_record(name: str, phone: str, email: str, date_of_birth: str, language: str = "English") -> str:
    """
    Create a new patient record during a voice call.
    
    Args:
        name: Patient's full name
        phone: Patient's phone number
        email: Patient's email address
        date_of_birth: Date of birth in YYYY-MM-DD format
        language: Preferred language (English or Spanish)
        
    Returns:
        JSON string with new patient details or error message
    """
    try:
        # Create minimal patient record with basic information
        # Other details can be filled in later during the appointment
        patient_data = PatientCreate(
            name=name,
            email=email,
            phone=phone,
            date_of_birth=date_of_birth,
            address={
                "street": "To be updated",
                "city": "To be updated",
                "state": "CA",
                "zip_code": "00000"
            },
            insurance={
                "provider": "To be updated",
                "policy_number": "To be updated",
                "group_number": "To be updated"
            },
            medical_history={
                "allergies": [],
                "conditions": [],
                "last_visit": None,
                "notes": "New patient - details to be collected during first visit"
            },
            preferences={
                "language": language,
                "communication_method": "phone",
                "reminder_time": "morning"
            },
            emergency_contact={
                "name": "To be updated",
                "relationship": "To be updated",
                "phone": "To be updated"
            }
        )
        
        patient = await db_manager.create_patient(patient_data)
        
        return json.dumps({
            "success": True,
            "patient_id": patient.id,
            "name": patient.name,
            "phone": patient.phone,
            "email": patient.email,
            "language_preference": patient.preferences.language,
            "message": f"New patient record created for {name}. Additional details can be collected during the first visit."
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to create patient record: {str(e)}"
        })


async def get_clinic_availability(date: str) -> str:
    """
    Check clinic availability for a specific date.
    
    Args:
        date: Date to check in YYYY-MM-DD format
        
    Returns:
        JSON string with availability information
    """
    try:
        appointments = await db_manager.get_appointments_by_date(date)
        
        # Define clinic hours and appointment slots
        clinic_hours = [
            "9:00 AM", "9:30 AM", "10:00 AM", "10:30 AM", "11:00 AM", "11:30 AM",
            "1:00 PM", "1:30 PM", "2:00 PM", "2:30 PM", "3:00 PM", "3:30 PM", "4:00 PM"
        ]
        
        # Get booked times
        booked_times = [apt.time for apt in appointments]
        
        # Calculate available slots
        available_slots = [time for time in clinic_hours if time not in booked_times]
        
        return json.dumps({
            "date": date,
            "total_slots": len(clinic_hours),
            "booked_slots": len(booked_times),
            "available_slots": len(available_slots),
            "available_times": available_slots[:5],  # Show first 5 available slots
            "is_fully_booked": len(available_slots) == 0,
            "next_available": available_slots[0] if available_slots else "No slots available"
        })
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to check availability: {str(e)}"
        )


# Function schema definitions (converted from TypeScript interfaces)
WEATHER_SCHEMA = FunctionSchema(
    name="get_weather_from_coords",
    type="function",
    description="Get the current weather from geographic coordinates",
    parameters={
        "type": "object",
        "properties": {
            "latitude": {
                "type": "number",
                "description": "Geographic latitude coordinate"
            },
            "longitude": {
                "type": "number", 
                "description": "Geographic longitude coordinate"
            }
        },
        "required": ["latitude", "longitude"]
    }
)

PATIENT_DETAILS_SCHEMA = FunctionSchema(
    name="get_patient_details",
    type="function",
    description="Get patient details by name for appointment scheduling and medical history",
    parameters={
        "type": "object",
        "properties": {
            "patient_name": {
                "type": "string",
                "description": "Full name of the patient to look up"
            }
        },
        "required": ["patient_name"]
    }
)

SCHEDULE_APPOINTMENT_SCHEMA = FunctionSchema(
    name="schedule_appointment",
    type="function",
    description="Schedule a new appointment for a patient",
    parameters={
        "type": "object",
        "properties": {
            "patient_name": {
                "type": "string",
                "description": "Full name of the patient"
            },
            "appointment_type": {
                "type": "string",
                "description": "Type of appointment (e.g., Emergency Consultation, Routine Cleaning, Root Canal, Check-up)"
            },
            "date": {
                "type": "string",
                "description": "Appointment date in YYYY-MM-DD format"
            },
            "time": {
                "type": "string",
                "description": "Appointment time (e.g., 2:30 PM, 10:00 AM)"
            },
            "priority": {
                "type": "string",
                "description": "Priority level: routine, treatment, or emergency",
                "enum": ["routine", "treatment", "emergency"]
            }
        },
        "required": ["patient_name", "appointment_type", "date", "time"]
    }
)

GET_APPOINTMENTS_SCHEMA = FunctionSchema(
    name="get_appointments_for_date",
    type="function",
    description="Get all appointments scheduled for a specific date",
    parameters={
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "description": "Date to check appointments for in YYYY-MM-DD format"
            }
        },
        "required": ["date"]
    }
)

EMERGENCY_CASE_SCHEMA = FunctionSchema(
    name="record_emergency_case",
    type="function",
    description="Record a new emergency dental case with triage assessment",
    parameters={
        "type": "object",
        "properties": {
            "patient_name": {
                "type": "string",
                "description": "Name of the patient"
            },
            "phone": {
                "type": "string",
                "description": "Patient's phone number"
            },
            "symptoms": {
                "type": "string",
                "description": "Description of dental symptoms or emergency"
            },
            "pain_level": {
                "type": "integer",
                "description": "Pain level from 1-10 (10 being most severe)",
                "minimum": 1,
                "maximum": 10
            },
            "duration": {
                "type": "string",
                "description": "How long the symptoms have persisted (e.g., '2 hours', '1 day')"
            }
        },
        "required": ["patient_name", "phone", "symptoms", "pain_level", "duration"]
    }
)

CREATE_PATIENT_SCHEMA = FunctionSchema(
    name="create_patient_record",
    type="function",
    description="Create a new patient record for first-time callers",
    parameters={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "Patient's full name"
            },
            "phone": {
                "type": "string",
                "description": "Patient's phone number"
            },
            "email": {
                "type": "string",
                "description": "Patient's email address"
            },
            "date_of_birth": {
                "type": "string",
                "description": "Date of birth in YYYY-MM-DD format"
            },
            "language": {
                "type": "string",
                "description": "Preferred language for communication",
                "enum": ["English", "Spanish"]
            }
        },
        "required": ["name", "phone", "email", "date_of_birth"]
    }
)

CLINIC_AVAILABILITY_SCHEMA = FunctionSchema(
    name="get_clinic_availability",
    type="function",
    description="Check available appointment slots for a specific date",
    parameters={
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "description": "Date to check availability for in YYYY-MM-DD format"
            }
        },
        "required": ["date"]
    }
)

class FunctionRegistry:
    """
    Registry for managing function handlers and their schemas.
    
    Converted from TypeScript array-based approach to a more structured
    Python class-based registry pattern.
    """
    
    def __init__(self):
        self._functions: Dict[str, Dict[str, Any]] = {}
        self._register_default_functions()
    
    def _register_default_functions(self):
        """Register the default set of functions"""
        # Original functions
        self.register_function(
            schema=WEATHER_SCHEMA,
            handler=get_weather_from_coords
        )
        
        # Eev AI Dental Clinic functions
        self.register_function(
            schema=PATIENT_DETAILS_SCHEMA,
            handler=get_patient_details
        )
        
        self.register_function(
            schema=SCHEDULE_APPOINTMENT_SCHEMA,
            handler=schedule_appointment
        )
        
        self.register_function(
            schema=GET_APPOINTMENTS_SCHEMA,
            handler=get_appointments_for_date
        )
        
        self.register_function(
            schema=EMERGENCY_CASE_SCHEMA,
            handler=record_emergency_case
        )
        
        self.register_function(
            schema=CREATE_PATIENT_SCHEMA,
            handler=create_patient_record
        )
        
        self.register_function(
            schema=CLINIC_AVAILABILITY_SCHEMA,
            handler=get_clinic_availability
        )
    
    def register_function(self, schema: FunctionSchema, handler):
        """
        Register a new function with its schema and handler.
        
        Args:
            schema: OpenAI function schema
            handler: Async function implementation
        """
        self._functions[schema.name] = {
            "schema": schema,
            "handler": handler
        }
    
    def get_function_schemas(self) -> List[FunctionSchema]:
        """
        Get all registered function schemas.
        
        Returns:
            List of function schemas for OpenAI API
        """
        return [func_data["schema"] for func_data in self._functions.values()]
    
    async def call_function(self, name: str, arguments: str) -> str:
        """
        Call a registered function with the provided arguments.
        
        Converted from TypeScript promise-based approach to Python async/await.
        
        Args:
            name: Function name to call
            arguments: JSON string of function arguments
            
        Returns:
            JSON string result from function execution
        """
        if name not in self._functions:
            return json.dumps({
                "error": f"No handler found for function: {name}"
            })
        
        try:
            # Parse arguments (equivalent to JSON.parse in TypeScript)
            args = json.loads(arguments)
        except json.JSONDecodeError:
            return json.dumps({
                "error": "Invalid JSON arguments for function call"
            })
        
        try:
            handler = self._functions[name]["handler"]
            
            # Call the handler with unpacked arguments
            if isinstance(args, dict):
                result = await handler(**args)
            else:
                result = await handler(args)
                
            return result
            
        except Exception as e:
            return json.dumps({
                "error": f"Error running function {name}: {str(e)}"
            })


# Global function registry instance
function_registry = FunctionRegistry()


def get_function_schemas() -> List[FunctionSchema]:
    """
    Get all available function schemas.
    
    Equivalent to the default export array in TypeScript version.
    """
    return function_registry.get_function_schemas()


async def handle_function_call(name: str, arguments: str) -> str:
    """
    Handle a function call from the OpenAI Realtime API.
    
    Converted from TypeScript handleFunctionCall function.
    
    Args:
        name: Function name
        arguments: JSON string of arguments
        
    Returns:
        JSON string result
    """
    return await function_registry.call_function(name, arguments)


# Global function registry instance
function_registry = FunctionRegistry()


def get_function_schemas() -> List[FunctionSchema]:
    """
    Get all available function schemas.
    
    Equivalent to the default export array in TypeScript version.
    """
    return function_registry.get_function_schemas()


async def handle_function_call(name: str, arguments: str) -> str:
    """
    Handle a function call from the OpenAI Realtime API.
    
    Converted from TypeScript handleFunctionCall function.
    
    Args:
        name: Function name
        arguments: JSON string of arguments
        
    Returns:
        JSON string result
    """
    return await function_registry.call_function(name, arguments)
