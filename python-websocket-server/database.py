"""
Database operations for Eev AI Dental Clinic Platform.

This module handles all database interactions using in-memory storage for development.
In production, this would be replaced with actual database operations.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from models import (
    Patient, PatientCreate, PatientUpdate,
    Appointment, AppointmentCreate, AppointmentUpdate,
    Reminder, ReminderCreate,
    EmergencyCase, EmergencyCreate,
    PatientSearchQuery, AppointmentSearchQuery,
    AppointmentStatus, AppointmentPriority, BookingMethod,
    ReminderType, ReminderMethod, ReminderStatus, Language,
    EmergencyPriority
)

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages all database operations for the Eev AI platform.
    Uses in-memory storage for development/demo purposes.
    """
    
    def __init__(self):
        """Initialize with sample data"""
        self._init_sample_data()
        logger.info("Database manager initialized with sample data")
    
    def _init_sample_data(self):
        """Initialize with comprehensive sample data"""
        # Sample patients
        self.patients = [
            {
                "id": 1,
                "name": "Maria Rodriguez",
                "email": "maria.rodriguez@email.com",
                "phone": "+1 (555) 123-4567",
                "date_of_birth": "1985-03-15",
                "address": {
                    "street": "123 Main St",
                    "city": "Los Angeles",
                    "state": "CA",
                    "zip_code": "90210"
                },
                "insurance": {
                    "provider": "Blue Cross Blue Shield",
                    "policy_number": "BC123456789",
                    "group_number": "GRP001"
                },
                "medical_history": {
                    "allergies": ["Penicillin"],
                    "conditions": ["Diabetes Type 2"],
                    "last_visit": "2024-01-15",
                    "notes": "Prefers Spanish communication, diabetic considerations needed"
                },
                "preferences": {
                    "language": "Spanish",
                    "communication_method": "phone",
                    "reminder_time": "morning"
                },
                "emergency_contact": {
                    "name": "Carlos Rodriguez",
                    "relationship": "Husband",
                    "phone": "+1 (555) 123-4568"
                },
                "created_at": datetime(2024, 1, 1, 10, 0, 0),
                "updated_at": datetime(2024, 1, 15, 14, 30, 0)
            },
            {
                "id": 2,
                "name": "John Smith",
                "email": "john.smith@email.com",
                "phone": "+1 (555) 234-5678",
                "date_of_birth": "1978-07-22",
                "address": {
                    "street": "456 Oak Ave",
                    "city": "Beverly Hills",
                    "state": "CA",
                    "zip_code": "90212"
                },
                "insurance": {
                    "provider": "Aetna",
                    "policy_number": "AET987654321",
                    "group_number": "GRP002"
                },
                "medical_history": {
                    "allergies": [],
                    "conditions": ["Hypertension"],
                    "last_visit": "2024-01-10",
                    "notes": "Regular patient, prefers email communication"
                },
                "preferences": {
                    "language": "English",
                    "communication_method": "email",
                    "reminder_time": "afternoon"
                },
                "emergency_contact": {
                    "name": "Jane Smith",
                    "relationship": "Wife",
                    "phone": "+1 (555) 234-5679"
                },
                "created_at": datetime(2023, 12, 15, 9, 0, 0),
                "updated_at": datetime(2024, 1, 10, 11, 15, 0)
            },
            {
                "id": 3,
                "name": "Sarah Johnson",
                "email": "sarah.johnson@email.com",
                "phone": "+1 (555) 345-6789",
                "date_of_birth": "1992-11-08",
                "address": {
                    "street": "789 Pine St",
                    "city": "Santa Monica",
                    "state": "CA",
                    "zip_code": "90401"
                },
                "insurance": {
                    "provider": "Cigna",
                    "policy_number": "CIG456789123",
                    "group_number": "GRP003"
                },
                "medical_history": {
                    "allergies": ["Latex"],
                    "conditions": ["TMJ"],
                    "last_visit": "2024-01-05",
                    "notes": "Young professional, prefers text communication"
                },
                "preferences": {
                    "language": "English",
                    "communication_method": "sms",
                    "reminder_time": "evening"
                },
                "emergency_contact": {
                    "name": "Michael Johnson",
                    "relationship": "Brother",
                    "phone": "+1 (555) 345-6790"
                },
                "created_at": datetime(2023, 11, 20, 16, 30, 0),
                "updated_at": datetime(2024, 1, 5, 13, 45, 0)
            }
        ]
        
        # Sample appointments
        self.appointments = [
            {
                "id": 1,
                "patient_name": "Maria Rodriguez",
                "patient_id": 1,
                "type": "Emergency Consultation",
                "date": "2024-01-25",
                "time": "2:30 PM",
                "duration": 60,
                "status": "scheduled",
                "priority": "emergency",
                "booked_via": "voice_agent",
                "notes": "Severe tooth pain, possible abscess",
                "created_at": datetime(2024, 1, 24, 14, 30, 0),
                "updated_at": datetime(2024, 1, 24, 14, 30, 0)
            },
            {
                "id": 2,
                "patient_name": "John Smith",
                "patient_id": 2,
                "type": "Routine Cleaning",
                "date": "2024-01-26",
                "time": "10:00 AM",
                "duration": 45,
                "status": "confirmed",
                "priority": "routine",
                "booked_via": "voice_agent",
                "notes": "Regular 6-month cleaning",
                "created_at": datetime(2024, 1, 20, 9, 15, 0),
                "updated_at": datetime(2024, 1, 22, 16, 20, 0)
            },
            {
                "id": 3,
                "patient_name": "Sarah Johnson",
                "patient_id": 3,
                "type": "Root Canal",
                "date": "2024-01-26",
                "time": "2:00 PM",
                "duration": 90,
                "status": "scheduled",
                "priority": "treatment",
                "booked_via": "online",
                "notes": "Follow-up for tooth #14",
                "created_at": datetime(2024, 1, 18, 11, 0, 0),
                "updated_at": datetime(2024, 1, 18, 11, 0, 0)
            },
            {
                "id": 4,
                "patient_name": "Michael Brown",
                "patient_id": 4,
                "type": "Check-up",
                "date": "2024-01-27",
                "time": "9:00 AM",
                "duration": 30,
                "status": "confirmed",
                "priority": "routine",
                "booked_via": "voice_agent",
                "notes": "Annual check-up",
                "created_at": datetime(2024, 1, 15, 8, 30, 0),
                "updated_at": datetime(2024, 1, 23, 10, 45, 0)
            }
        ]
        
        # Sample reminders
        self.reminders = [
            {
                "id": 1,
                "patient_name": "John Smith",
                "patient_id": 2,
                "type": "appointment",
                "method": "voice_call",
                "scheduled_for": datetime(2024, 1, 25, 9, 0, 0),
                "appointment_date": datetime(2024, 1, 26, 10, 0, 0),
                "status": "sent",
                "response": "confirmed",
                "language": "English",
                "template_used": "appointment_en",
                "created_at": datetime(2024, 1, 24, 15, 0, 0),
                "sent_at": datetime(2024, 1, 25, 9, 0, 0)
            },
            {
                "id": 2,
                "patient_name": "Maria Rodriguez",
                "patient_id": 1,
                "type": "appointment",
                "method": "voice_call",
                "scheduled_for": datetime(2024, 1, 25, 13, 0, 0),
                "appointment_date": datetime(2024, 1, 25, 14, 30, 0),
                "status": "pending",
                "response": None,
                "language": "Spanish",
                "template_used": "appointment_es",
                "created_at": datetime(2024, 1, 24, 14, 30, 0),
                "sent_at": None
            },
            {
                "id": 3,
                "patient_name": "Sarah Johnson",
                "patient_id": 3,
                "type": "follow_up",
                "method": "sms",
                "scheduled_for": datetime(2024, 1, 28, 18, 0, 0),
                "appointment_date": None,
                "status": "scheduled",
                "response": None,
                "language": "English",
                "template_used": "follow_up_en",
                "created_at": datetime(2024, 1, 26, 14, 0, 0),
                "sent_at": None
            }
        ]
        
        # Sample emergency cases
        self.emergency_cases = [
            {
                "id": 1,
                "patient_name": "Maria Rodriguez",
                "patient_id": 1,
                "phone": "+1 (555) 123-4567",
                "symptoms": "Severe tooth pain, swelling on right side of face",
                "pain_level": 9,
                "duration": "2 hours",
                "status": "active",
                "priority": "critical",
                "ai_assessment": "Possible severe abscess - immediate attention required",
                "next_action": "Emergency appointment scheduled for 2:30 PM today",
                "escalated_to": None,
                "created_at": datetime(2024, 1, 24, 12, 30, 0),
                "resolved_at": None
            },
            {
                "id": 2,
                "patient_name": "Robert Wilson",
                "patient_id": None,
                "phone": "+1 (555) 456-7890",
                "symptoms": "Knocked out tooth from sports injury",
                "pain_level": 8,
                "duration": "30 minutes",
                "status": "escalated",
                "priority": "high",
                "ai_assessment": "Dental trauma - emergency evaluation needed",
                "next_action": "Referred to emergency dental service",
                "escalated_to": "Dr. Emergency Service",
                "created_at": datetime(2024, 1, 23, 19, 15, 0),
                "resolved_at": None
            },
            {
                "id": 3,
                "patient_name": "Lisa Chen",
                "patient_id": None,
                "phone": "+1 (555) 789-0123",
                "symptoms": "Mild toothache, sensitivity to cold",
                "pain_level": 4,
                "duration": "1 day",
                "status": "resolved",
                "priority": "low",
                "ai_assessment": "Mild discomfort - routine appointment appropriate",
                "next_action": "Routine appointment scheduled for next week",
                "escalated_to": None,
                "created_at": datetime(2024, 1, 22, 10, 0, 0),
                "resolved_at": datetime(2024, 1, 22, 10, 15, 0)
            }
        ]
        
        # Initialize counters for new IDs
        self.next_patient_id = max([p["id"] for p in self.patients], default=0) + 1
        self.next_appointment_id = max([a["id"] for a in self.appointments], default=0) + 1
        self.next_reminder_id = max([r["id"] for r in self.reminders], default=0) + 1
        self.next_emergency_id = max([e["id"] for e in self.emergency_cases], default=0) + 1
    
    # Patient Operations
    async def create_patient(self, patient_data: PatientCreate) -> Patient:
        """Create a new patient record"""
        try:
            patient_dict = patient_data.dict()
            patient_dict["id"] = self.next_patient_id
            patient_dict["created_at"] = datetime.utcnow()
            patient_dict["updated_at"] = datetime.utcnow()
            
            self.patients.append(patient_dict)
            self.next_patient_id += 1
            
            return Patient(**patient_dict)
                
        except Exception as e:
            logger.error(f"Error creating patient: {e}")
            raise
    
    async def get_patient(self, patient_id: int) -> Optional[Patient]:
        """Get patient by ID"""
        try:
            patient_dict = next((p for p in self.patients if p["id"] == patient_id), None)
            if patient_dict:
                return Patient(**patient_dict)
            return None
            
        except Exception as e:
            logger.error(f"Error getting patient {patient_id}: {e}")
            return None
    
    async def search_patients(self, query: PatientSearchQuery) -> List[Patient]:
        """Search patients with filters"""
        try:
            filtered_patients = self.patients
            
            if query.name:
                filtered_patients = [p for p in filtered_patients 
                                   if query.name.lower() in p["name"].lower()]
            if query.phone:
                filtered_patients = [p for p in filtered_patients 
                                   if query.phone in p["phone"]]
            if query.email:
                filtered_patients = [p for p in filtered_patients 
                                   if query.email.lower() in p["email"].lower()]
            
            # Apply pagination
            start = query.offset
            end = start + query.limit
            paginated_patients = filtered_patients[start:end]
            
            return [Patient(**patient) for patient in paginated_patients]
            
        except Exception as e:
            logger.error(f"Error searching patients: {e}")
            return []
    
    async def update_patient(self, patient_id: int, patient_data: PatientUpdate) -> Optional[Patient]:
        """Update patient record"""
        try:
            patient_dict = next((p for p in self.patients if p["id"] == patient_id), None)
            if not patient_dict:
                return None
            
            # Update only non-None fields
            update_dict = {k: v for k, v in patient_data.dict().items() if v is not None}
            update_dict["updated_at"] = datetime.utcnow()
            
            patient_dict.update(update_dict)
            return Patient(**patient_dict)
            
        except Exception as e:
            logger.error(f"Error updating patient {patient_id}: {e}")
            return None
    
    async def delete_patient(self, patient_id: int) -> bool:
        """Delete patient record"""
        try:
            original_length = len(self.patients)
            self.patients = [p for p in self.patients if p["id"] != patient_id]
            return len(self.patients) < original_length
            
        except Exception as e:
            logger.error(f"Error deleting patient {patient_id}: {e}")
            return False
    
    # Appointment Operations
    async def create_appointment(self, appointment_data: AppointmentCreate) -> Appointment:
        """Create a new appointment"""
        try:
            appointment_dict = appointment_data.dict()
            appointment_dict["id"] = self.next_appointment_id
            appointment_dict["created_at"] = datetime.utcnow()
            appointment_dict["updated_at"] = datetime.utcnow()
            
            self.appointments.append(appointment_dict)
            self.next_appointment_id += 1
            
            return Appointment(**appointment_dict)
                
        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            raise
    
    async def get_appointments_by_date(self, target_date: str) -> List[Appointment]:
        """Get all appointments for a specific date"""
        try:
            filtered_appointments = [a for a in self.appointments if a["date"] == target_date]
            return [Appointment(**apt) for apt in filtered_appointments]
            
        except Exception as e:
            logger.error(f"Error getting appointments for {target_date}: {e}")
            return []
    
    async def get_patient_appointments(self, patient_id: int) -> List[Appointment]:
        """Get all appointments for a patient"""
        try:
            filtered_appointments = [a for a in self.appointments if a["patient_id"] == patient_id]
            return [Appointment(**apt) for apt in filtered_appointments]
            
        except Exception as e:
            logger.error(f"Error getting appointments for patient {patient_id}: {e}")
            return []
    
    async def update_appointment(self, appointment_id: int, appointment_data: AppointmentUpdate) -> Optional[Appointment]:
        """Update appointment record"""
        try:
            appointment_dict = next((a for a in self.appointments if a["id"] == appointment_id), None)
            if not appointment_dict:
                return None
            
            update_dict = {k: v for k, v in appointment_data.dict().items() if v is not None}
            update_dict["updated_at"] = datetime.utcnow()
            
            appointment_dict.update(update_dict)
            return Appointment(**appointment_dict)
            
        except Exception as e:
            logger.error(f"Error updating appointment {appointment_id}: {e}")
            return None
    
    async def delete_appointment(self, appointment_id: int) -> bool:
        """Delete appointment"""
        try:
            original_length = len(self.appointments)
            self.appointments = [a for a in self.appointments if a["id"] != appointment_id]
            return len(self.appointments) < original_length
            
        except Exception as e:
            logger.error(f"Error deleting appointment {appointment_id}: {e}")
            return False
    
    # Reminder Operations
    async def create_reminder(self, reminder_data: ReminderCreate) -> Reminder:
        """Create a new reminder"""
        try:
            reminder_dict = reminder_data.dict()
            reminder_dict["id"] = self.next_reminder_id
            reminder_dict["created_at"] = datetime.utcnow()
            reminder_dict["status"] = "scheduled"
            
            self.reminders.append(reminder_dict)
            self.next_reminder_id += 1
            
            return Reminder(**reminder_dict)
                
        except Exception as e:
            logger.error(f"Error creating reminder: {e}")
            raise
    
    async def get_pending_reminders(self) -> List[Reminder]:
        """Get all pending reminders"""
        try:
            now = datetime.utcnow()
            pending_reminders = [
                r for r in self.reminders 
                if r["status"] == "scheduled" and r["scheduled_for"] <= now
            ]
            
            return [Reminder(**reminder) for reminder in pending_reminders]
            
        except Exception as e:
            logger.error(f"Error getting pending reminders: {e}")
            return []
    
    async def update_reminder_status(self, reminder_id: int, status: str, response: Optional[str] = None) -> bool:
        """Update reminder status and response"""
        try:
            reminder_dict = next((r for r in self.reminders if r["id"] == reminder_id), None)
            if not reminder_dict:
                return False
            
            reminder_dict["status"] = status
            reminder_dict["sent_at"] = datetime.utcnow()
            if response:
                reminder_dict["response"] = response
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating reminder {reminder_id}: {e}")
            return False
    
    # Emergency Case Operations
    async def create_emergency_case(self, emergency_data: EmergencyCreate) -> EmergencyCase:
        """Create a new emergency case"""
        try:
            # Determine priority based on pain level
            if emergency_data.pain_level >= 9:
                priority = "critical"
            elif emergency_data.pain_level >= 7:
                priority = "high"
            elif emergency_data.pain_level >= 5:
                priority = "medium"
            else:
                priority = "low"
            
            # Generate AI assessment based on symptoms and pain level
            ai_assessment = self._generate_ai_assessment(emergency_data)
            next_action = self._determine_next_action(emergency_data.pain_level)
            
            emergency_dict = emergency_data.dict()
            emergency_dict.update({
                "id": self.next_emergency_id,
                "priority": priority,
                "ai_assessment": ai_assessment,
                "next_action": next_action,
                "status": "active",
                "created_at": datetime.utcnow()
            })
            
            self.emergency_cases.append(emergency_dict)
            self.next_emergency_id += 1
            
            return EmergencyCase(**emergency_dict)
                
        except Exception as e:
            logger.error(f"Error creating emergency case: {e}")
            raise
    
    async def get_active_emergencies(self) -> List[EmergencyCase]:
        """Get all active emergency cases"""
        try:
            active_cases = [e for e in self.emergency_cases if e["status"] == "active"]
            # Sort by creation time, most recent first
            active_cases.sort(key=lambda x: x["created_at"], reverse=True)
            
            return [EmergencyCase(**case) for case in active_cases]
            
        except Exception as e:
            logger.error(f"Error getting active emergencies: {e}")
            return []
    
    async def escalate_emergency(self, case_id: int, escalated_to: str) -> bool:
        """Escalate emergency case"""
        try:
            case_dict = next((e for e in self.emergency_cases if e["id"] == case_id), None)
            if not case_dict:
                return False
            
            case_dict["status"] = "escalated"
            case_dict["escalated_to"] = escalated_to
            
            return True
            
        except Exception as e:
            logger.error(f"Error escalating emergency {case_id}: {e}")
            return False
    
    # Analytics Operations
    async def get_call_metrics_by_hour(self, target_date: str) -> List[Dict[str, Any]]:
        """Get hourly call metrics for analytics"""
        try:
            # Sample metrics data for demonstration
            sample_metrics = [
                {"hour": "8 AM", "total_calls": 12, "resolved_calls": 11, "average_duration": 3.2, "emergency_calls": 1},
                {"hour": "9 AM", "total_calls": 18, "resolved_calls": 17, "average_duration": 2.8, "emergency_calls": 2},
                {"hour": "10 AM", "total_calls": 22, "resolved_calls": 21, "average_duration": 3.1, "emergency_calls": 0},
                {"hour": "11 AM", "total_calls": 25, "resolved_calls": 24, "average_duration": 2.9, "emergency_calls": 1},
                {"hour": "12 PM", "total_calls": 20, "resolved_calls": 19, "average_duration": 3.5, "emergency_calls": 0},
                {"hour": "1 PM", "total_calls": 15, "resolved_calls": 14, "average_duration": 2.7, "emergency_calls": 1},
                {"hour": "2 PM", "total_calls": 28, "resolved_calls": 26, "average_duration": 3.0, "emergency_calls": 2},
                {"hour": "3 PM", "total_calls": 24, "resolved_calls": 23, "average_duration": 2.6, "emergency_calls": 0}
            ]
            return sample_metrics
            
        except Exception as e:
            logger.error(f"Error getting call metrics: {e}")
            return []
    
    def _generate_ai_assessment(self, emergency_data: EmergencyCreate) -> str:
        """Generate AI assessment based on symptoms and pain level"""
        symptoms_lower = emergency_data.symptoms.lower()
        pain_level = emergency_data.pain_level
        
        if pain_level >= 9:
            if "swelling" in symptoms_lower or "abscess" in symptoms_lower:
                return "Possible severe abscess - immediate attention required"
            elif "trauma" in symptoms_lower or "accident" in symptoms_lower:
                return "Dental trauma - emergency evaluation needed"
            else:
                return "Severe pain - urgent dental care required"
        elif pain_level >= 7:
            if "sensitivity" in symptoms_lower:
                return "Severe sensitivity - possible nerve involvement"
            elif "bleeding" in symptoms_lower:
                return "Bleeding with pain - requires prompt attention"
            else:
                return "Significant pain - same-day appointment recommended"
        elif pain_level >= 5:
            return "Moderate pain - schedule within 24-48 hours"
        else:
            return "Mild discomfort - routine appointment appropriate"
    
    def _determine_next_action(self, pain_level: int) -> str:
        """Determine next action based on pain level"""
        if pain_level >= 9:
            return "Emergency appointment scheduled for today"
        elif pain_level >= 7:
            return "Same-day appointment recommended"
        elif pain_level >= 5:
            return "Schedule within 24-48 hours"
        else:
            return "Routine appointment scheduling"


# Global database manager instance
db_manager = DatabaseManager()


# Convenience functions for use throughout the application
async def get_patient_by_id(patient_id: int) -> Optional[Patient]:
    """Get patient by ID"""
    return await db_manager.get_patient(patient_id)


async def search_patients_by_name(name: str) -> List[Patient]:
    """Search patients by name"""
    query = PatientSearchQuery(name=name)
    return await db_manager.search_patients(query)


async def get_today_appointments() -> List[Appointment]:
    """Get today's appointments"""
    today = date.today().isoformat()
    return await db_manager.get_appointments_by_date(today)


async def create_emergency_from_call(patient_name: str, phone: str, symptoms: str, pain_level: int, duration: str) -> EmergencyCase:
    """Create emergency case from voice call"""
    emergency_data = EmergencyCreate(
        patient_name=patient_name,
        phone=phone,
        symptoms=symptoms,
        pain_level=pain_level,
        duration=duration
    )
    return await db_manager.create_emergency_case(emergency_data)