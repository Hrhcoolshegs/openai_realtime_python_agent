"""
Enhanced Type definitions for Eev AI Dental Clinic Platform

This module defines comprehensive data structures for the dental clinic management system.
Includes patient records, appointments, reminders, emergency cases, and analytics data.
"""

from typing import Optional, Dict, Any, List, Literal
from dataclasses import dataclass
from pydantic import BaseModel, Field, EmailStr
from fastapi import WebSocket
from datetime import datetime, date, time
from enum import Enum


@dataclass
class Session:
    """
    Session data structure to maintain connection state.
    
    Holds references to active WebSocket connections and session data.
    """
    twilio_conn: Optional[WebSocket] = None
    frontend_conn: Optional[WebSocket] = None
    model_conn: Optional[WebSocket] = None
    stream_sid: Optional[str] = None
    saved_config: Optional[Dict[str, Any]] = None
    last_assistant_item: Optional[str] = None
    response_start_timestamp: Optional[int] = None
    latest_media_timestamp: Optional[int] = None
    openai_api_key: Optional[str] = None


# Enums for better type safety
class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class AppointmentPriority(str, Enum):
    ROUTINE = "routine"
    TREATMENT = "treatment"
    EMERGENCY = "emergency"


class BookingMethod(str, Enum):
    VOICE_AGENT = "voice_agent"
    ONLINE = "online"
    PHONE = "phone"
    WALK_IN = "walk_in"


class ReminderType(str, Enum):
    APPOINTMENT = "appointment"
    FOLLOW_UP = "follow_up"
    INSURANCE = "insurance"


class ReminderMethod(str, Enum):
    VOICE_CALL = "voice_call"
    EMAIL = "email"
    SMS = "sms"


class ReminderStatus(str, Enum):
    SCHEDULED = "scheduled"
    SENT = "sent"
    PENDING = "pending"
    CONFIRMED = "confirmed"
    DECLINED = "declined"
    FAILED = "failed"


class EmergencyPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Language(str, Enum):
    ENGLISH = "English"
    SPANISH = "Spanish"


# Patient Management Models
class Address(BaseModel):
    """Patient address information"""
    street: str
    city: str
    state: str
    zip_code: str = Field(alias="zipCode")


class Insurance(BaseModel):
    """Patient insurance information"""
    provider: str
    policy_number: str = Field(alias="policyNumber")
    group_number: str = Field(alias="groupNumber")


class MedicalHistory(BaseModel):
    """Patient medical history"""
    allergies: List[str] = Field(default_factory=list)
    conditions: List[str] = Field(default_factory=list)
    last_visit: Optional[str] = Field(alias="lastVisit", default=None)
    notes: str = ""


class Preferences(BaseModel):
    """Patient communication preferences"""
    language: Language = Language.ENGLISH
    communication_method: str = Field(alias="communicationMethod", default="phone")
    reminder_time: str = Field(alias="reminderTime", default="morning")


class EmergencyContact(BaseModel):
    """Patient emergency contact information"""
    name: str
    relationship: str
    phone: str


class Patient(BaseModel):
    """Complete patient record"""
    id: Optional[int] = None
    name: str
    email: EmailStr
    phone: str
    date_of_birth: str = Field(alias="dateOfBirth")
    address: Address
    insurance: Insurance
    medical_history: MedicalHistory = Field(alias="medicalHistory")
    preferences: Preferences
    emergency_contact: EmergencyContact = Field(alias="emergencyContact")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True


class PatientCreate(BaseModel):
    """Patient creation model (without ID)"""
    name: str
    email: EmailStr
    phone: str
    date_of_birth: str
    address: Address
    insurance: Insurance
    medical_history: MedicalHistory
    preferences: Preferences
    emergency_contact: EmergencyContact


class PatientUpdate(BaseModel):
    """Patient update model (all fields optional)"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    date_of_birth: Optional[str] = None
    address: Optional[Address] = None
    insurance: Optional[Insurance] = None
    medical_history: Optional[MedicalHistory] = None
    preferences: Optional[Preferences] = None
    emergency_contact: Optional[EmergencyContact] = None


# Appointment Management Models
class Appointment(BaseModel):
    """Complete appointment record"""
    id: Optional[int] = None
    patient_name: str = Field(alias="patientName")
    patient_id: int = Field(alias="patientId")
    type: str
    date: str
    time: str
    duration: int  # in minutes
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    priority: AppointmentPriority = AppointmentPriority.ROUTINE
    booked_via: BookingMethod = Field(alias="bookedVia", default=BookingMethod.ONLINE)
    notes: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True


class AppointmentCreate(BaseModel):
    """Appointment creation model"""
    patient_name: str
    patient_id: int
    type: str
    date: str
    time: str
    duration: int
    priority: AppointmentPriority = AppointmentPriority.ROUTINE
    booked_via: BookingMethod = BookingMethod.ONLINE
    notes: str = ""


class AppointmentUpdate(BaseModel):
    """Appointment update model"""
    patient_name: Optional[str] = None
    patient_id: Optional[int] = None
    type: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    duration: Optional[int] = None
    status: Optional[AppointmentStatus] = None
    priority: Optional[AppointmentPriority] = None
    booked_via: Optional[BookingMethod] = None
    notes: Optional[str] = None


# Reminder System Models
class Reminder(BaseModel):
    """Automated reminder record"""
    id: Optional[int] = None
    patient_name: str = Field(alias="patientName")
    patient_id: int = Field(alias="patientId")
    type: ReminderType
    method: ReminderMethod
    scheduled_for: datetime = Field(alias="scheduledFor")
    appointment_date: Optional[datetime] = Field(alias="appointmentDate", default=None)
    status: ReminderStatus = ReminderStatus.SCHEDULED
    response: Optional[str] = None
    language: Language = Language.ENGLISH
    template_used: Optional[str] = Field(alias="templateUsed", default=None)
    created_at: Optional[datetime] = None
    sent_at: Optional[datetime] = Field(alias="sentAt", default=None)

    class Config:
        allow_population_by_field_name = True


class ReminderCreate(BaseModel):
    """Reminder creation model"""
    patient_name: str
    patient_id: int
    type: ReminderType
    method: ReminderMethod
    scheduled_for: datetime
    appointment_date: Optional[datetime] = None
    language: Language = Language.ENGLISH


# Emergency Triage Models
class EmergencyCase(BaseModel):
    """Emergency triage case record"""
    id: Optional[int] = None
    patient_name: str = Field(alias="patientName")
    patient_id: Optional[int] = Field(alias="patientId", default=None)
    phone: str
    symptoms: str
    pain_level: int = Field(alias="painLevel", ge=1, le=10)
    duration: str
    status: Literal["active", "escalated", "resolved"] = "active"
    priority: EmergencyPriority
    ai_assessment: str = Field(alias="aiAssessment")
    next_action: str = Field(alias="nextAction")
    escalated_to: Optional[str] = Field(alias="escalatedTo", default=None)
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = Field(alias="resolvedAt", default=None)

    class Config:
        allow_population_by_field_name = True


class EmergencyCreate(BaseModel):
    """Emergency case creation model"""
    patient_name: str
    patient_id: Optional[int] = None
    phone: str
    symptoms: str
    pain_level: int = Field(ge=1, le=10)
    duration: str


# Analytics Models
class CallMetrics(BaseModel):
    """Call analytics metrics"""
    total_calls: int
    resolved_calls: int
    average_duration: float
    emergency_calls: int
    hour: str


class IntentMetrics(BaseModel):
    """AI intent detection metrics"""
    intent: str
    count: int
    accuracy: float
    color: str


class PerformanceMetrics(BaseModel):
    """Overall performance metrics"""
    patient_satisfaction: float
    first_call_resolution: float
    escalation_rate: float
    average_call_duration: str
    calls_per_hour: float
    wait_time_reduction: float
    spanish_calls_handled: float
    accessibility_features_used: float
    multilingual_accuracy: float


# OpenAI Function Call Models
class FunctionCallItem(BaseModel):
    """Function call item from OpenAI"""
    name: str
    arguments: str
    call_id: Optional[str] = None


class FunctionSchema(BaseModel):
    """OpenAI function schema definition"""
    name: str
    type: str = "function"
    description: Optional[str] = None
    parameters: Dict[str, Any]


class FunctionHandler(BaseModel):
    """Function handler with schema and implementation"""
    schema: FunctionSchema
    
    class Config:
        arbitrary_types_allowed = True


# API Response Models
class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None


class ToolListResponse(BaseModel):
    """Response model for /tools endpoint"""
    tools: List[FunctionSchema]


class PublicUrlResponse(BaseModel):
    """Response model for /public-url endpoint"""
    public_url: str


# Twilio WebSocket message types
class TwilioStartMessage(BaseModel):
    """Twilio WebSocket start message structure"""
    event: str = "start"
    start: Dict[str, Any]


class TwilioMediaMessage(BaseModel):
    """Twilio WebSocket media message structure"""
    event: str = "media"
    media: Dict[str, Any]


class TwilioCloseMessage(BaseModel):
    """Twilio WebSocket close message structure"""
    event: str = "close"


# OpenAI Realtime API message types
class OpenAIInputAudioMessage(BaseModel):
    """OpenAI input audio buffer message"""
    type: str = "input_audio_buffer.append"
    audio: str


class OpenAIResponseMessage(BaseModel):
    """OpenAI response message structure"""
    type: str
    response: Optional[Dict[str, Any]] = None


# Frontend WebSocket message types
class FrontendConfigMessage(BaseModel):
    """Frontend configuration message"""
    type: str = "configure"
    config: Dict[str, Any]


# Database query models
class PatientSearchQuery(BaseModel):
    """Patient search parameters"""
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    limit: int = Field(default=50, le=100)
    offset: int = Field(default=0, ge=0)


class AppointmentSearchQuery(BaseModel):
    """Appointment search parameters"""
    date: Optional[str] = None
    patient_id: Optional[int] = None
    status: Optional[AppointmentStatus] = None
    priority: Optional[AppointmentPriority] = None
    limit: int = Field(default=50, le=100)
    offset: int = Field(default=0, ge=0)


class DateRangeQuery(BaseModel):
    """Date range query for analytics"""
    start_date: str
    end_date: str