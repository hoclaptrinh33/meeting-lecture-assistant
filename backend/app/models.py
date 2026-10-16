import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    LargeBinary,
    PrimaryKeyConstraint,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    display_name = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    # Relationships
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    live_sessions = relationship("LiveSession", back_populates="user", cascade="all, delete-orphan")
    voice_profiles = relationship("VoiceProfile", back_populates="user", cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash = Column(Text, nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="refresh_tokens")

    __table_args__ = (
        Index("refresh_tokens_user_idx", "user_id"),
    )


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(Text, nullable=False)
    source = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    error_code = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    warnings = Column(JSONB, nullable=False, default=list)
    audio_path = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    vocabulary = Column(Text, nullable=True)
    num_speakers = Column(Integer, nullable=True)
    diarization_device = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime(timezone=True), nullable=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="jobs")
    segments = relationship("Segment", back_populates="job", cascade="all, delete-orphan")
    speaker_aliases = relationship("SpeakerAlias", back_populates="job", cascade="all, delete-orphan")
    job_events = relationship("JobEvent", back_populates="job", cascade="all, delete-orphan")
    llm_runs = relationship("LlmRun", back_populates="job", cascade="all, delete-orphan")
    media_tokens = relationship("MediaToken", back_populates="job", cascade="all, delete-orphan")
    highlights = relationship("Highlight", back_populates="job", cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="job", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("source IN ('upload', 'live')", name="chk_jobs_source"),
        CheckConstraint(
            "status IN ('queued', 'capturing', 'preprocessing', 'transcribing', 'diarizing', 'ready', 'failed', 'cancelled')",
            name="chk_jobs_status",
        ),
        CheckConstraint("num_speakers BETWEEN 1 AND 20", name="chk_jobs_num_speakers"),
        CheckConstraint("diarization_device IN ('cuda', 'cpu')", name="chk_jobs_diarization_device"),
        Index("jobs_user_created_idx", "user_id", created_at.desc()),
    )


class LiveSession(Base):
    __tablename__ = "live_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)
    title = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    vocabulary = Column(Text, nullable=True)
    num_speakers = Column(Integer, nullable=True)
    pcm_path = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    ended_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="live_sessions")
    job = relationship("Job")
    ws_tickets = relationship("WsTicket", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("status IN ('capturing', 'stopping', 'finalized', 'failed')", name="chk_live_status"),
        CheckConstraint("num_speakers BETWEEN 1 AND 20", name="chk_live_num_speakers"),
        Index("live_sessions_job_idx", "job_id"),
    )


class Segment(Base):
    __tablename__ = "segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    pass_number = Column("pass", SmallInteger, nullable=False)
    position = Column(Integer, nullable=False)
    start_ms = Column(Integer, nullable=False)
    end_ms = Column(Integer, nullable=False)
    text_raw = Column(Text, nullable=False)
    text_cleaned = Column(Text, nullable=True)
    text_edited = Column(Text, nullable=True)
    speaker_label = Column(Text, nullable=True)

    job = relationship("Job", back_populates="segments")
    words = relationship("Word", back_populates="segment", cascade="all, delete-orphan")
    highlights = relationship("Highlight", back_populates="segment", cascade="all, delete-orphan")
    action_items = relationship("ActionItem", back_populates="segment")

    __table_args__ = (
        CheckConstraint('"pass" IN (1, 2)', name="chk_segments_pass"),
        UniqueConstraint("job_id", "pass", "position", name="uq_segments_job_pass_pos"),
    )


class Word(Base):
    __tablename__ = "words"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    segment_id = Column(UUID(as_uuid=True), ForeignKey("segments.id", ondelete="CASCADE"), nullable=False)
    position = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    start_ms = Column(Integer, nullable=False)
    end_ms = Column(Integer, nullable=False)
    speaker_label = Column(Text, nullable=True)

    segment = relationship("Segment", back_populates="words")

    __table_args__ = (
        UniqueConstraint("segment_id", "position", name="uq_words_segment_pos"),
    )


class SpeakerAlias(Base):
    __tablename__ = "speaker_aliases"

    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), primary_key=True)
    speaker_label = Column(Text, primary_key=True)
    display_name = Column(Text, nullable=False)
    source = Column(Text, nullable=False)

    job = relationship("Job", back_populates="speaker_aliases")

    __table_args__ = (
        CheckConstraint("source IN ('manual', 'voice_profile')", name="chk_speaker_aliases_source"),
    )


class JobEvent(Base):
    __tablename__ = "job_events"

    id = Column(BigInteger, Identity(always=True), primary_key=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    seq = Column(Integer, nullable=False)
    event_type = Column(Text, nullable=False)
    payload = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    job = relationship("Job", back_populates="job_events")

    __table_args__ = (
        UniqueConstraint("job_id", "seq", name="uq_job_events_job_seq"),
    )


class LlmRun(Base):
    __tablename__ = "llm_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    task = Column(Text, nullable=False)
    template = Column(Text, nullable=True)
    status = Column(Text, nullable=False)
    model_name = Column(Text, nullable=True)
    result = Column(JSONB, nullable=True)
    error_code = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    finished_at = Column(DateTime(timezone=True), nullable=True)

    job = relationship("Job", back_populates="llm_runs")
    shards = relationship("LlmMapShard", back_populates="llm_run", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("task IN ('clean', 'summarize')", name="chk_llm_runs_task"),
        CheckConstraint("template IN ('meeting', 'lecture')", name="chk_llm_runs_template"),
        CheckConstraint("status IN ('running', 'done', 'failed')", name="chk_llm_runs_status"),
        CheckConstraint("task = 'clean' OR template IS NOT NULL", name="chk_llm_template"),
        Index("llm_runs_job_task_created_idx", "job_id", "task", created_at.desc()),
    )


class LlmMapShard(Base):
    __tablename__ = "llm_map_shards"

    run_id = Column(UUID(as_uuid=True), ForeignKey("llm_runs.id", ondelete="CASCADE"), primary_key=True)
    shard_index = Column(Integer, primary_key=True)
    input_start_ms = Column(Integer, nullable=False)
    input_end_ms = Column(Integer, nullable=False)
    status = Column(Text, nullable=False)
    result = Column(JSONB, nullable=True)

    llm_run = relationship("LlmRun", back_populates="shards")

    __table_args__ = (
        CheckConstraint("status IN ('running', 'done', 'failed')", name="chk_llm_shards_status"),
    )


class MediaToken(Base):
    __tablename__ = "media_tokens"

    token_hash = Column(Text, primary_key=True)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    job = relationship("Job", back_populates="media_tokens")

    __table_args__ = (
        Index("media_tokens_job_idx", "job_id"),
    )


class WsTicket(Base):
    __tablename__ = "ws_tickets"

    token_hash = Column(Text, primary_key=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("live_sessions.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    session = relationship("LiveSession", back_populates="ws_tickets")

    __table_args__ = (
        Index("ws_tickets_session_idx", "session_id"),
    )


class VoiceProfile(Base):
    __tablename__ = "voice_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    display_name = Column(Text, nullable=False)
    status = Column(Text, nullable=False)
    embedding = Column(LargeBinary, nullable=True)
    embedding_dim = Column(Integer, nullable=True)
    embedding_model = Column(Text, nullable=True)
    sample_path = Column(Text, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="voice_profiles")

    __table_args__ = (
        CheckConstraint("status IN ('processing', 'ready', 'failed')", name="chk_voice_status"),
        Index("voice_profiles_user_idx", "user_id"),
    )


class Highlight(Base):
    __tablename__ = "highlights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    segment_id = Column(UUID(as_uuid=True), ForeignKey("segments.id", ondelete="CASCADE"), nullable=False)
    quote = Column(Text, nullable=False)
    start_ms = Column(Integer, nullable=False)
    end_ms = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    job = relationship("Job", back_populates="highlights")
    segment = relationship("Segment", back_populates="highlights")

    __table_args__ = (
        Index("highlights_job_idx", "job_id", "created_at"),
    )


class ActionItem(Base):
    __tablename__ = "action_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    segment_id = Column(UUID(as_uuid=True), ForeignKey("segments.id", ondelete="SET NULL"), nullable=True)
    start_ms = Column(Integer, nullable=True)
    owner = Column(Text, nullable=False, default="")
    task = Column(Text, nullable=False)
    deadline = Column(Text, nullable=False, default="")
    source = Column(Text, nullable=False, default="manual")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    job = relationship("Job", back_populates="action_items")
    segment = relationship("Segment", back_populates="action_items")

    __table_args__ = (
        CheckConstraint("source IN ('manual')", name="chk_action_items_source"),
        Index("action_items_job_idx", "job_id", "created_at"),
    )
