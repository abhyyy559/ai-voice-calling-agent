from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contacts'
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'))
    name = Column(String)
    phone = Column(String)
    external_id = Column(String)
    custom_fields = Column(JSON)
    status = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class Campaign(Base):
    __tablename__ = 'campaigns'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    domain_config_id = Column(Integer, ForeignKey('domain_configs.id'))
    status = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class DomainConfig(Base):
    __tablename__ = 'domain_configs'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    config = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class Call(Base):
    __tablename__ = 'calls'
    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey('campaigns.id'))
    contact_id = Column(Integer, ForeignKey('contacts.id'))
    status = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration = Column(Float)
    cost = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

class CallEvent(Base):
    __tablename__ = 'call_events'
    id = Column(Integer, primary_key=True)
    call_id = Column(Integer, ForeignKey('calls.id'))
    event_type = Column(String)
    details = Column(JSON)
    created_at = Column(DateTime, server_default=func.now())

class Transcript(Base):
    __tablename__ = 'transcripts'
    id = Column(Integer, primary_key=True)
    call_id = Column(Integer, ForeignKey('calls.id'))
    content = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class ExtractedField(Base):
    __tablename__ = 'extracted_fields'
    id = Column(Integer, primary_key=True)
    call_id = Column(Integer, ForeignKey('calls.id'))
    field_name = Column(String)
    value = Column(String)
    confidence = Column(Float)
    created_at = Column(DateTime, server_default=func.now())

class ConsentRecord(Base):
    __tablename__ = 'consent_records'
    id = Column(Integer, primary_key=True)
    contact_id = Column(Integer, ForeignKey('contacts.id'))
    consent_type = Column(String)
    consent_given = Column(Boolean)
    obtained_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
