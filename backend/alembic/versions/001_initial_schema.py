"""initial_schema

Revision ID: 001_initial
Revises: 
Create Date: 2026-10-16 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.Text(), nullable=False, unique=True),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('display_name', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )

    # 2. refresh_tokens
    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('token_hash', sa.Text(), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('refresh_tokens_user_idx', 'refresh_tokens', ['user_id'])

    # 3. jobs
    op.create_table(
        'jobs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('source', sa.Text(), sa.CheckConstraint("source IN ('upload', 'live')"), nullable=False),
        sa.Column('status', sa.Text(), sa.CheckConstraint(
            "status IN ('queued', 'capturing', 'preprocessing', 'transcribing', 'diarizing', 'ready', 'failed', 'cancelled')"
        ), nullable=False),
        sa.Column('error_code', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('warnings', postgresql.JSONB(), server_default='[]', nullable=False),
        sa.Column('audio_path', sa.Text(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('vocabulary', sa.Text(), nullable=True),
        sa.Column('num_speakers', sa.Integer(), sa.CheckConstraint("num_speakers BETWEEN 1 AND 20"), nullable=True),
        sa.Column('diarization_device', sa.Text(), sa.CheckConstraint("diarization_device IN ('cuda', 'cpu')"), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('jobs_user_created_idx', 'jobs', ['user_id', sa.text('created_at DESC')])

    # 4. live_sessions
    op.create_table(
        'live_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), sa.CheckConstraint("status IN ('capturing', 'stopping', 'finalized', 'failed')"), nullable=False),
        sa.Column('vocabulary', sa.Text(), nullable=True),
        sa.Column('num_speakers', sa.Integer(), sa.CheckConstraint("num_speakers BETWEEN 1 AND 20"), nullable=True),
        sa.Column('pcm_path', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('live_sessions_job_idx', 'live_sessions', ['job_id'])

    # 5. segments
    op.create_table(
        'segments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('pass', sa.SmallInteger(), sa.CheckConstraint('"pass" IN (1, 2)'), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('start_ms', sa.Integer(), nullable=False),
        sa.Column('end_ms', sa.Integer(), nullable=False),
        sa.Column('text_raw', sa.Text(), nullable=False),
        sa.Column('text_cleaned', sa.Text(), nullable=True),
        sa.Column('text_edited', sa.Text(), nullable=True),
        sa.Column('speaker_label', sa.Text(), nullable=True),
        sa.UniqueConstraint('job_id', 'pass', 'position', name='uq_segments_job_pass_pos'),
    )

    # 6. words
    op.create_table(
        'words',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('segment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('segments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('start_ms', sa.Integer(), nullable=False),
        sa.Column('end_ms', sa.Integer(), nullable=False),
        sa.Column('speaker_label', sa.Text(), nullable=True),
        sa.UniqueConstraint('segment_id', 'position', name='uq_words_segment_pos'),
    )

    # 7. speaker_aliases
    op.create_table(
        'speaker_aliases',
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('speaker_label', sa.Text(), nullable=False),
        sa.Column('display_name', sa.Text(), nullable=False),
        sa.Column('source', sa.Text(), sa.CheckConstraint("source IN ('manual', 'voice_profile')"), nullable=False),
        sa.PrimaryKeyConstraint('job_id', 'speaker_label', name='pk_speaker_aliases'),
    )

    # 8. job_events
    op.create_table(
        'job_events',
        sa.Column('id', sa.BigInteger(), sa.Identity(always=True), primary_key=True),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('seq', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.Text(), nullable=False),
        sa.Column('payload', postgresql.JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('job_id', 'seq', name='uq_job_events_job_seq'),
    )

    # 9. llm_runs
    op.create_table(
        'llm_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('task', sa.Text(), sa.CheckConstraint("task IN ('clean', 'summarize')"), nullable=False),
        sa.Column('template', sa.Text(), sa.CheckConstraint("template IN ('meeting', 'lecture')"), nullable=True),
        sa.Column('status', sa.Text(), sa.CheckConstraint("status IN ('running', 'done', 'failed')"), nullable=False),
        sa.Column('model_name', sa.Text(), nullable=True),
        sa.Column('result', postgresql.JSONB(), nullable=True),
        sa.Column('error_code', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("task = 'clean' OR template IS NOT NULL", name='chk_llm_template'),
    )
    op.create_index('llm_runs_job_task_created_idx', 'llm_runs', ['job_id', 'task', sa.text('created_at DESC')])

    # 10. llm_map_shards
    op.create_table(
        'llm_map_shards',
        sa.Column('run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('llm_runs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('shard_index', sa.Integer(), nullable=False),
        sa.Column('input_start_ms', sa.Integer(), nullable=False),
        sa.Column('input_end_ms', sa.Integer(), nullable=False),
        sa.Column('status', sa.Text(), sa.CheckConstraint("status IN ('running', 'done', 'failed')"), nullable=False),
        sa.Column('result', postgresql.JSONB(), nullable=True),
        sa.PrimaryKeyConstraint('run_id', 'shard_index', name='pk_llm_map_shards'),
    )

    # 11. media_tokens
    op.create_table(
        'media_tokens',
        sa.Column('token_hash', sa.Text(), primary_key=True),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('media_tokens_job_idx', 'media_tokens', ['job_id'])

    # 12. ws_tickets
    op.create_table(
        'ws_tickets',
        sa.Column('token_hash', sa.Text(), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('live_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ws_tickets_session_idx', 'ws_tickets', ['session_id'])

    # 13. voice_profiles
    op.create_table(
        'voice_profiles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('display_name', sa.Text(), nullable=False),
        sa.Column('status', sa.Text(), sa.CheckConstraint("status IN ('processing', 'ready', 'failed')"), nullable=False),
        sa.Column('embedding', sa.LargeBinary(), nullable=True),
        sa.Column('embedding_dim', sa.Integer(), nullable=True),
        sa.Column('embedding_model', sa.Text(), nullable=True),
        sa.Column('sample_path', sa.Text(), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('voice_profiles_user_idx', 'voice_profiles', ['user_id'])

    # 14. highlights
    op.create_table(
        'highlights',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('segment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('segments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('quote', sa.Text(), nullable=False),
        sa.Column('start_ms', sa.Integer(), nullable=False),
        sa.Column('end_ms', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('highlights_job_idx', 'highlights', ['job_id', 'created_at'])

    # 15. action_items
    op.create_table(
        'action_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('job_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False),
        sa.Column('segment_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('segments.id', ondelete='SET NULL'), nullable=True),
        sa.Column('start_ms', sa.Integer(), nullable=True),
        sa.Column('owner', sa.Text(), server_default='', nullable=False),
        sa.Column('task', sa.Text(), nullable=False),
        sa.Column('deadline', sa.Text(), server_default='', nullable=False),
        sa.Column('source', sa.Text(), sa.CheckConstraint("source IN ('manual')"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('action_items_job_idx', 'action_items', ['job_id', 'created_at'])


def downgrade() -> None:
    op.drop_table('action_items')
    op.drop_table('highlights')
    op.drop_table('voice_profiles')
    op.drop_table('ws_tickets')
    op.drop_table('media_tokens')
    op.drop_table('llm_map_shards')
    op.drop_table('llm_runs')
    op.drop_table('job_events')
    op.drop_table('speaker_aliases')
    op.drop_table('words')
    op.drop_table('segments')
    op.drop_table('live_sessions')
    op.drop_table('jobs')
    op.drop_table('refresh_tokens')
    op.drop_table('users')
