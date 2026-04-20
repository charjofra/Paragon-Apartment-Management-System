import pytest
from utils.db_utils import get_db_connection
from unittest.mock import patch, MagicMock

def test_db_connection_handles_missing_database_flag():
    """
    Test that the connection builder correctly removes the 'database' key 
    when connect_to_db=False (usually used during initial database creation).
    """
    # Mocking mysql.connector so we don't actually need a local MySQL server running just to pass the test
    with patch('utils.db_utils.mysql.connector.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        # Call the utility function
        conn = get_db_connection(connect_to_db=False)
        
        # Ensure it attempted a connection
        mock_connect.assert_called_once()
        kwargs = mock_connect.call_args.kwargs
        
        # Verify the database parameter was stripped from the config
        assert 'database' not in kwargs

def test_execute_read_raises_exception_on_no_connection():
    """
    Test that execute_read correctly raises an exception when the database is unreachable,
    preventing silent failures.
    """
    from utils.db_utils import execute_read
    
    with patch('utils.db_utils.get_db_connection', return_value=None):
        with pytest.raises(Exception, match="Failed to connect to database"):
            execute_read("SELECT * FROM users")