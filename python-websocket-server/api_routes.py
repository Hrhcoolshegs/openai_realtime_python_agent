"""
API Routes for Eev AI Dental Clinic Platform.

This module defines all REST API endpoints for managing clinic data.
Provides CRUD operations for patients, appointments, reminders, and emergency cases.
"""

import logging
from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, HTTPException, Query, Path
from fastapi.responses import JSONResponse

from models import (
    Patient, PatientCreate, PatientUpdate,
    Appointment, AppointmentCreate, AppointmentUpdate,
    Reminder, ReminderCreate,
    EmergencyCase, EmergencyCreate,
    SuccessResponse, ErrorResponse,
    PatientSearchQuery, AppointmentSearchQuery
)
from database import db_manager

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1", tags=["Eev AI Dental Clinic"])


# Patient Management Endpoints
@router.post("/patients", response_model=Patient)
async def create_patient(patient_data: PatientCreate):
    """Create a new patient record"""
    try:
        patient = await db_manager.create_patient(patient_data)
        return patient
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/patients/{patient_id}", response_model=Optional[Patient])
async def get_patient(patient_id: int = Path(..., description="Patient ID")):
    """Get patient by ID"""
    patient = await db_manager.get_patient(patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.get("/patients", response_model=List[Patient])
async def search_patients(
    name: Optional[str] = Query(None, description="Search by patient name"),
    phone: Optional[str] = Query(None, description="Search by phone number"),
    email: Optional[str] = Query(None, description="Search by email"),
    limit: int = Query(50, le=100, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip")
):
    """Search patients with optional filters"""
    query = PatientSearchQuery(
        name=name,
        phone=phone,
        email=email,
        limit=limit,
        offset=offset
    )
    return await db_manager.search_patients(query)


@router.put("/patients/{patient_id}", response_model=Optional[Patient])
async def update_patient(
    patient_data: PatientUpdate,
    patient_id: int = Path(..., description="Patient ID")
):
    """Update patient record"""
    patient = await db_manager.update_patient(patient_id, patient_data)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient


@router.delete("/patients/{patient_id}")
async def delete_patient(patient_id: int = Path(..., description="Patient ID")):
    """Delete patient record"""
    success = await db_manager.delete_patient(patient_id)
    if not success:
        raise HTTPException(status_code=404, detail="Patient not found")
    return SuccessResponse(message="Patient deleted successfully")


# Appointment Management Endpoints
@router.post("/appointments", response_model=Appointment)
async def create_appointment(appointment_data: AppointmentCreate):
    """Create a new appointment"""
    try:
        appointment = await db_manager.create_appointment(appointment_data)
        return appointment
    except Exception as e:
        logger.error(f"Error creating appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/appointments", response_model=List[Appointment])
async def get_appointments(
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority")
):
    """Get appointments with optional filters"""
    try:
        if date:
            return await db_manager.get_appointments_by_date(date)
        elif patient_id:
            return await db_manager.get_patient_appointments(patient_id)
        else:
            # Get today's appointments by default
            today = date.today().isoformat()
            return await db_manager.get_appointments_by_date(today)
    except Exception as e:
        logger.error(f"Error getting appointments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/appointments/{appointment_id}", response_model=Optional[Appointment])
async def update_appointment(
    appointment_data: AppointmentUpdate,
    appointment_id: int = Path(..., description="Appointment ID")
):
    """Update appointment record"""
    appointment = await db_manager.update_appointment(appointment_id, appointment_data)
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment


@router.delete("/appointments/{appointment_id}")
async def delete_appointment(appointment_id: int = Path(..., description="Appointment ID")):
    """Delete appointment"""
    success = await db_manager.delete_appointment(appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return SuccessResponse(message="Appointment deleted successfully")


# Reminder Management Endpoints
@router.post("/reminders", response_model=Reminder)
async def create_reminder(reminder_data: ReminderCreate):
    """Create a new reminder"""
    try:
        reminder = await db_manager.create_reminder(reminder_data)
        return reminder
    except Exception as e:
        logger.error(f"Error creating reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reminders/pending", response_model=List[Reminder])
async def get_pending_reminders():
    """Get all pending reminders"""
    return await db_manager.get_pending_reminders()


@router.put("/reminders/{reminder_id}/status")
async def update_reminder_status(
    reminder_id: int = Path(..., description="Reminder ID"),
    status: str = Query(..., description="New status"),
    response: Optional[str] = Query(None, description="Patient response")
):
    """Update reminder status"""
    success = await db_manager.update_reminder_status(reminder_id, status, response)
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return SuccessResponse(message="Reminder status updated successfully")


# Emergency Triage Endpoints
@router.post("/emergency", response_model=EmergencyCase)
async def create_emergency_case(emergency_data: EmergencyCreate):
    """Create a new emergency case"""
    try:
        emergency = await db_manager.create_emergency_case(emergency_data)
        return emergency
    except Exception as e:
        logger.error(f"Error creating emergency case: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/emergency/active", response_model=List[EmergencyCase])
async def get_active_emergencies():
    """Get all active emergency cases"""
    return await db_manager.get_active_emergencies()


@router.put("/emergency/{case_id}/escalate")
async def escalate_emergency(
    case_id: int = Path(..., description="Emergency case ID"),
    escalated_to: str = Query(..., description="Who the case was escalated to")
):
    """Escalate emergency case"""
    success = await db_manager.escalate_emergency(case_id, escalated_to)
    if not success:
        raise HTTPException(status_code=404, detail="Emergency case not found")
    return SuccessResponse(message="Emergency case escalated successfully")


# Analytics Endpoints
@router.get("/analytics/metrics")
async def get_analytics_metrics(
    date: str = Query(default=None, description="Date for metrics (YYYY-MM-DD)")
):
    """Get analytics metrics for dashboard"""
    try:
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        
        # Get call metrics
        call_metrics = await db_manager.get_call_metrics_by_hour(target_date)
        
        # Calculate summary statistics
        total_calls = sum(metric["total_calls"] for metric in call_metrics)
        total_resolved = sum(metric["resolved_calls"] for metric in call_metrics)
        total_emergency = sum(metric["emergency_calls"] for metric in call_metrics)
        
        resolution_rate = (total_resolved / total_calls * 100) if total_calls > 0 else 0
        
        return {
            "date": target_date,
            "total_calls": total_calls,
            "resolution_rate": round(resolution_rate, 1),
            "emergency_calls": total_emergency,
            "hourly_metrics": call_metrics,
            "intent_analysis": [
                {"intent": "Appointment Booking", "count": 45, "accuracy": 96, "color": "bg-blue-500"},
                {"intent": "Emergency Triage", "count": 12, "accuracy": 100, "color": "bg-red-500"},
                {"intent": "Insurance Inquiry", "count": 28, "accuracy": 92, "color": "bg-green-500"},
                {"intent": "General Information", "count": 31, "accuracy": 89, "color": "bg-purple-500"},
                {"intent": "Appointment Modification", "count": 12, "accuracy": 94, "color": "bg-orange-500"},
                {"intent": "Prescription Inquiry", "count": 8, "accuracy": 87, "color": "bg-pink-500"}
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Dashboard Statistics Endpoint
@router.get("/dashboard/stats")
async def get_dashboard_stats():
    """Get real-time dashboard statistics"""
    try:
        today = date.today().isoformat()
        
        # Get today's appointments
        today_appointments = await db_manager.get_appointments_by_date(today)
        
        # Get active emergencies
        active_emergencies = await db_manager.get_active_emergencies()
        
        # Calculate statistics (these would be real queries in production)
        stats = {
            "active_voice_calls": 12,
            "patients_managed": 847,
            "todays_appointments": len(today_appointments),
            "emergency_escalations": len(active_emergencies),
            "ai_metrics": {
                "intent_accuracy": 98.7,
                "average_response_time": 2.3,
                "online_status": True
            }
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health check endpoint
@router.get("/health")
async def health_check():
    """Health check for the API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Eev AI Dental Clinic Backend"
    }