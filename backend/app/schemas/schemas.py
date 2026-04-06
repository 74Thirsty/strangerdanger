from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=10)
    household_name: str = Field(min_length=2, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class ChildCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class ChildOut(BaseModel):
    id: str
    name: str
    created_at: datetime


class DeviceEnrollmentCreate(BaseModel):
    child_id: str


class DeviceEnrollConsume(BaseModel):
    enrollment_code: str
    name: str
    platform: str = "android"


class DeviceOut(BaseModel):
    id: str
    child_id: str
    name: str
    platform: str


class SessionCreate(BaseModel):
    child_id: str
    device_id: str


class SessionOut(BaseModel):
    id: str
    child_id: str
    device_id: str
    active: bool


class LocationIngest(BaseModel):
    session_id: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy_m: float = Field(gt=0)
    confidence: int = Field(ge=0, le=100)
    idempotency_key: str = Field(min_length=4, max_length=128)


class GeofenceCreate(BaseModel):
    child_id: str
    name: str
    center_latitude: float = Field(ge=-90, le=90)
    center_longitude: float = Field(ge=-180, le=180)
    radius_m: float = Field(gt=10)


class PanicCreate(BaseModel):
    child_id: str
    session_id: str
    notes: str = ""


class AlertOut(BaseModel):
    id: str
    type: str
    payload: str
    read: bool
    created_at: datetime
