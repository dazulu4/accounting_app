# Database Migrations - Enterprise Edition

Professional database migration management using Alembic with enterprise features and multi-environment support.

## Features

- **Environment-aware configuration** with automatic database URL detection
- **Professional migration naming** with timestamps and descriptive messages
- **Multi-environment support** for development, staging, and production
- **Automatic backup creation** before migrations in non-development environments
- **Comprehensive logging** with structured output
- **Migration validation** and verification tools
- **MySQL optimization** with proper indexes and constraints

## Quick Start

### 1. Environment Setup

Ensure your environment variables are configured:

```bash
# Development (default values)
export APP_ENVIRONMENT=development
export DATABASE_HOST=localhost
export DATABASE_PORT=3306
export DATABASE_NAME=accounting_dev
export DATABASE_USERNAME=admin
export DATABASE_PASSWORD=admin123

# For staging/production, use appropriate values
```

### 2. Basic Migration Commands

```bash
# Apply all pending migrations
./scripts/migrate.sh upgrade development

# Check current migration status
./scripts/migrate.sh current development

# View migration history
./scripts/migrate.sh history development

# Create database backup
./scripts/migrate.sh backup production
```

### 3. Creating New Migrations

```bash
# Generate migration with autogenerate (recommended)
./scripts/generate-migration.sh "add_user_preferences_table" --auto

# Create empty migration template
./scripts/generate-migration.sh "custom_data_migration"
```

## Migration Scripts

### `scripts/migrate.sh`

Professional migration execution script with the following commands:

- **`upgrade`** - Apply pending migrations
- **`downgrade`** - Rollback last migration
- **`current`** - Show current migration version
- **`history`** - Show migration history
- **`backup`** - Create database backup
- **`validate`** - Validate migration environment

**Usage:**
```bash
./scripts/migrate.sh [command] [environment]
```

**Examples:**
```bash
./scripts/migrate.sh upgrade production
./scripts/migrate.sh current staging
./scripts/migrate.sh backup production
```

### `scripts/generate-migration.sh`

Migration generation script with validation and templates:

**Usage:**
```bash
./scripts/generate-migration.sh [message] [--auto]
```

**Examples:**
```bash
./scripts/generate-migration.sh "create_audit_log_table" --auto
./scripts/generate-migration.sh "add_user_email_index"
```

## Configuration Files

### `alembic.ini`

Enterprise-grade Alembic configuration with:
- Professional migration file naming with timestamps
- MySQL-specific engine configuration
- Environment-specific settings
- Comprehensive logging configuration

### `migration/env.py`

Environment-aware migration configuration with:
- Automatic database URL detection from environment variables
- Enterprise database connection with pooling
- Structured logging integration
- Multi-environment support
- Proper error handling

## Migration File Structure

Migrations follow enterprise naming conventions:
```
YYYYMMDD_HHMM_revision_message.py
```

Example: `20250119_1430_ba4800daf143_create_tasks_table_enterprise.py`

## Database Schema

### Tasks Table

The main tasks table with enterprise-grade schema design:

```sql
CREATE TABLE tasks (
    task_id CHAR(36) NOT NULL COMMENT 'Unique task identifier (UUID)',
    title VARCHAR(200) NOT NULL COMMENT 'Task title or summary',
    description TEXT NOT NULL COMMENT 'Detailed task description',
    user_id INTEGER NOT NULL COMMENT 'ID of the user who owns this task',
    status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT 'Task status',
    priority VARCHAR(10) NOT NULL DEFAULT 'medium' COMMENT 'Task priority',
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    completed_at DATETIME(6) NULL COMMENT 'Task completion timestamp',
    
    PRIMARY KEY (task_id),
    INDEX idx_tasks_user_id (user_id),
    INDEX idx_tasks_status (status),
    INDEX idx_tasks_user_status (user_id, status),
    INDEX idx_tasks_priority (priority),
    INDEX idx_tasks_created_at (created_at),
    INDEX idx_tasks_completed (status, completed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

## Environment-Specific Configuration

### Development
- Local MySQL database
- Migration logging enabled
- No automatic backups
- Relaxed validation

### Staging
- Staging database with SSL
- Automatic backups before migrations
- Migration validation required
- Performance monitoring

### Production
- Production database with high availability
- Mandatory backups before any migration
- Extra confirmation for destructive operations
- Comprehensive audit logging
- Rollback procedures documented

## Best Practices

### Migration Creation
1. **Use descriptive names** in snake_case format
2. **Test migrations** in development first
3. **Review generated migrations** before applying
4. **Include rollback procedures** for complex migrations
5. **Document data migrations** with comments

### Migration Execution
1. **Always backup** before production migrations
2. **Test in staging** environment first
3. **Monitor performance** during large migrations
4. **Have rollback plan** ready
5. **Coordinate with team** for production deployments

### Naming Conventions
- **Creating tables**: `create_[table_name]_table`
- **Adding columns**: `add_[column_name]_to_[table_name]`
- **Removing columns**: `remove_[column_name]_from_[table_name]`
- **Adding indexes**: `add_index_[table_name]_[column_name]`
- **Data migrations**: `migrate_[description]_data`

## Troubleshooting

### Common Issues

**Migration fails with connection error:**
```bash
# Verify environment variables
./scripts/migrate.sh validate development

# Check database connectivity
mysql -h $DATABASE_HOST -u $DATABASE_USERNAME -p$DATABASE_PASSWORD $DATABASE_NAME
```

**Autogenerate not detecting changes:**
```bash
# Verify models are properly imported
python -c "from infrastructure.driven_adapters.repositories.base import Base; print(Base.metadata.tables.keys())"
```

**Migration conflicts:**
```bash
# Check current state
./scripts/migrate.sh current development

# View migration history
./scripts/migrate.sh history development
```

### Recovery Procedures

**Rollback last migration:**
```bash
./scripts/migrate.sh downgrade [environment]
```

**Restore from backup:**
```bash
# For production (requires DBA assistance)
mysql -h $DATABASE_HOST -u $DATABASE_USERNAME -p$DATABASE_PASSWORD $DATABASE_NAME < backup_file.sql
```

## Monitoring and Maintenance

- **Regular backup verification** for production environments
- **Migration performance monitoring** for large tables
- **Index usage analysis** after schema changes
- **Database size monitoring** after migrations
- **Regular cleanup** of old backup files

## Support

For migration issues or questions:
1. Check this documentation
2. Review migration logs
3. Validate environment configuration
4. Test in development environment first
5. Contact database team for production issues 