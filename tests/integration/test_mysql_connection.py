"""
MySQL Connection Integration Test - Enterprise Edition

Integration test to verify MySQL database connectivity and table existence
using the enterprise database configuration and synchronous operations.
"""

import pytest
from sqlalchemy import text

from infrastructure.helpers.database.connection import database_connection
from infrastructure.helpers.logger.logger_config import get_logger

# Configure logger
logger = get_logger(__name__)


@pytest.mark.integration
@pytest.mark.database
class TestMySQLConnection:
    """Integration tests for MySQL database connectivity"""
    
    def test_mysql_basic_connection(self):
        """
        Test basic MySQL connection using enterprise configuration
        """
        logger.info("testing_mysql_basic_connection")
        
        # Test basic connection
        with database_connection.create_session() as session:
            result = session.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            
            assert row is not None, "No result obtained from SELECT 1"
            assert row[0] == 1, "SELECT 1 result is not 1"
        
        logger.info("mysql_basic_connection_successful")
    
    def test_mysql_database_verification(self):
        """
        Test current database name verification
        """
        logger.info("testing_mysql_database_verification")
        
        with database_connection.create_session() as session:
            result = session.execute(text("SELECT DATABASE() as db_name"))
            db_name = result.fetchone()[0]
            
            # Allow for test database naming variations
            expected_databases = ["accounting", "accounting_test", "accounting_dev"]
            assert db_name in expected_databases, (
                f"Current database is '{db_name}', expected one of {expected_databases}"
            )
        
        logger.info("mysql_database_verification_successful", database=db_name)
    
    def test_mysql_tables_existence(self):
        """
        Test that required tables exist in the database
        """
        logger.info("testing_mysql_tables_existence")
        
        with database_connection.create_session() as session:
            # Check for tables
            result = session.execute(text("SHOW TABLES"))
            tables = result.fetchall()
            table_names = [table[0] for table in tables]
            
            assert len(tables) > 0, "No tables found in the accounting database"
            
            # Check for specific required tables
            required_tables = ["tasks", "alembic_version"]
            for required_table in required_tables:
                assert required_table in table_names, (
                    f"Required table '{required_table}' not found. "
                    f"Available tables: {table_names}"
                )
        
        logger.info(
            "mysql_tables_existence_verified",
            total_tables=len(table_names),
            tables=table_names
        )
    
    def test_mysql_tasks_table_structure(self):
        """
        Test tasks table structure matches expected schema
        """
        logger.info("testing_mysql_tasks_table_structure")
        
        with database_connection.create_session() as session:
            # Check tasks table structure
            result = session.execute(text("DESCRIBE tasks"))
            columns = result.fetchall()
            column_names = [column[0] for column in columns]
            
            # Expected columns in tasks table
            expected_columns = [
                "task_id", "title", "description", "user_id", 
                "status", "priority", "created_at", "updated_at", "completed_at"
            ]
            
            for expected_column in expected_columns:
                assert expected_column in column_names, (
                    f"Expected column '{expected_column}' not found in tasks table. "
                    f"Available columns: {column_names}"
                )
        
        logger.info(
            "mysql_tasks_table_structure_verified",
            columns=column_names
        )
    
    def test_mysql_connection_pooling(self):
        """
        Test connection pooling behavior
        """
        logger.info("testing_mysql_connection_pooling")
        
        # Test multiple concurrent connections
        sessions = []
        try:
            for i in range(3):
                session = database_connection.create_session()
                sessions.append(session)
                
                # Execute query on each session
                result = session.execute(text("SELECT CONNECTION_ID() as conn_id"))
                conn_id = result.fetchone()[0]
                
                logger.debug("connection_established", session_index=i, connection_id=conn_id)
            
            # All sessions should work
            assert len(sessions) == 3, "Not all sessions were created"
            
        finally:
            # Clean up sessions
            for session in sessions:
                session.close()
        
        logger.info("mysql_connection_pooling_successful")


# Legacy compatibility function
@pytest.mark.integration
@pytest.mark.database
def test_mysql_connection():
    """
    Legacy test function for backward compatibility
    
    Note: This function is deprecated. Use TestMySQLConnection class instead.
    """
    logger.warning("using_legacy_mysql_connection_test")
    
    # Use the new enterprise test
    test_instance = TestMySQLConnection()
    test_instance.test_mysql_basic_connection()
    test_instance.test_mysql_database_verification()
    test_instance.test_mysql_tables_existence() 