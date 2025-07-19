"""Create tasks table - Enterprise Edition

Revision ID: ba4800daf143
Revises: 
Create Date: 2025-01-19 14:30:00.000000

This migration creates the tasks table with enterprise-grade schema design
including proper indexes, constraints, and data types optimized for MySQL.

Features:
- UUID primary key for scalability
- Optimized column types and lengths
- Proper indexes for performance
- Enterprise naming conventions
- MySQL-specific optimizations
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'ba4800daf143'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create tasks table with enterprise schema design
    """
    # Create tasks table
    op.create_table(
        'tasks',
        
        # Primary Key - UUID for scalability
        sa.Column(
            'task_id', 
            mysql.CHAR(36), 
            nullable=False,
            comment='Unique task identifier (UUID)'
        ),
        
        # Required Business Fields
        sa.Column(
            'title', 
            mysql.VARCHAR(200), 
            nullable=False,
            comment='Task title or summary'
        ),
        sa.Column(
            'description', 
            mysql.TEXT, 
            nullable=False,
            comment='Detailed task description'
        ),
        sa.Column(
            'user_id', 
            mysql.INTEGER, 
            nullable=False,
            comment='ID of the user who owns this task'
        ),
        
        # Status and Priority
        sa.Column(
            'status', 
            mysql.VARCHAR(20), 
            nullable=False, 
            default='pending',
            comment='Task status: pending, in_progress, completed, cancelled'
        ),
        sa.Column(
            'priority', 
            mysql.VARCHAR(10), 
            nullable=False, 
            default='medium',
            comment='Task priority: low, medium, high, urgent'
        ),
        
        # Timestamps
        sa.Column(
            'created_at', 
            mysql.DATETIME(fsp=6), 
            nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP(6)'),
            comment='Task creation timestamp'
        ),
        sa.Column(
            'updated_at', 
            mysql.DATETIME(fsp=6), 
            nullable=False,
            server_default=sa.text('CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)'),
            comment='Last update timestamp'
        ),
        sa.Column(
            'completed_at', 
            mysql.DATETIME(fsp=6), 
            nullable=True,
            comment='Task completion timestamp'
        ),
        
        # Primary Key Constraint
        sa.PrimaryKeyConstraint('task_id', name='pk_tasks'),
        
        # Table configuration for MySQL
        mysql_engine='InnoDB',
        mysql_charset='utf8mb4',
        mysql_collate='utf8mb4_unicode_ci',
        comment='Tasks table - stores user tasks with status tracking'
    )
    
    # Create Performance Indexes
    
    # Index for user_id lookups (most common query pattern)
    op.create_index(
        'idx_tasks_user_id', 
        'tasks', 
        ['user_id'],
        comment='Index for user-based task queries'
    )
    
    # Index for status filtering
    op.create_index(
        'idx_tasks_status', 
        'tasks', 
        ['status'],
        comment='Index for status-based filtering'
    )
    
    # Composite index for user + status queries
    op.create_index(
        'idx_tasks_user_status', 
        'tasks', 
        ['user_id', 'status'],
        comment='Composite index for user + status queries'
    )
    
    # Index for priority-based sorting
    op.create_index(
        'idx_tasks_priority', 
        'tasks', 
        ['priority'],
        comment='Index for priority-based queries'
    )
    
    # Index for timestamp-based queries (recent tasks, etc.)
    op.create_index(
        'idx_tasks_created_at', 
        'tasks', 
        ['created_at'],
        comment='Index for timestamp-based queries'
    )
    
    # Composite index for completed tasks
    op.create_index(
        'idx_tasks_completed', 
        'tasks', 
        ['status', 'completed_at'],
        comment='Index for completed task queries'
    )


def downgrade() -> None:
    """
    Drop tasks table and all associated indexes
    """
    # Drop all indexes first
    op.drop_index('idx_tasks_completed', table_name='tasks')
    op.drop_index('idx_tasks_created_at', table_name='tasks')
    op.drop_index('idx_tasks_priority', table_name='tasks')
    op.drop_index('idx_tasks_user_status', table_name='tasks')
    op.drop_index('idx_tasks_status', table_name='tasks')
    op.drop_index('idx_tasks_user_id', table_name='tasks')
    
    # Drop the table
    op.drop_table('tasks')
