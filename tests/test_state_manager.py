"""
Unit Tests for State Manager

Tests session state initialization, getters, setters, and validation.

Reference: Planning/STREAMLIT_TECHNICAL_GUIDELINES.md - Testing
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Mock streamlit for testing
class MockSessionState(dict):
    """Mock Streamlit session state"""
    pass

class MockStreamlit:
    """Mock Streamlit module"""
    session_state = MockSessionState()

sys.modules['streamlit'] = MockStreamlit()

from streamlit_utils.state_manager import (
    init_session_state,
    get_workflow_step,
    set_workflow_step,
    get_project_name,
    set_project_name,
    get_uploaded_files,
    get_parameters,
    set_parameters,
    validate_state,
    reset_session_state,
    can_proceed_to_next_step,
)


class TestStateInitialization:
    """Test session state initialization"""
    
    def test_init_session_state(self):
        """Test that init_session_state creates all required keys"""
        MockStreamlit.session_state.clear()
        init_session_state()
        
        assert "workflow_step" in MockStreamlit.session_state
        assert "project_name" in MockStreamlit.session_state
        assert "uploaded_files" in MockStreamlit.session_state
        assert "parameters" in MockStreamlit.session_state
        assert "processing_status" in MockStreamlit.session_state
        assert "generated_masks" in MockStreamlit.session_state
        assert "alignment_result" in MockStreamlit.session_state
        assert "results_summary" in MockStreamlit.session_state
    
    def test_init_session_state_idempotent(self):
        """Test that init_session_state is idempotent"""
        MockStreamlit.session_state.clear()
        init_session_state()
        first_state = dict(MockStreamlit.session_state)
        
        init_session_state()
        second_state = dict(MockStreamlit.session_state)
        
        assert first_state == second_state


class TestWorkflowStep:
    """Test workflow step getters and setters"""
    
    def setup_method(self):
        """Setup for each test"""
        MockStreamlit.session_state.clear()
        init_session_state()
    
    def test_get_workflow_step_default(self):
        """Test default workflow step is 0"""
        assert get_workflow_step() == 0
    
    def test_set_workflow_step(self):
        """Test setting workflow step"""
        set_workflow_step(3)
        assert get_workflow_step() == 3
    
    def test_set_workflow_step_invalid(self):
        """Test setting invalid workflow step raises error"""
        with pytest.raises(ValueError):
            set_workflow_step(7)
        
        with pytest.raises(ValueError):
            set_workflow_step(-1)
    
    def test_workflow_step_range(self):
        """Test all valid workflow steps"""
        for step in range(7):
            set_workflow_step(step)
            assert get_workflow_step() == step


class TestProjectName:
    """Test project name getters and setters"""
    
    def setup_method(self):
        """Setup for each test"""
        MockStreamlit.session_state.clear()
        init_session_state()
    
    def test_get_project_name_default(self):
        """Test default project name is empty"""
        assert get_project_name() == ""
    
    def test_set_project_name(self):
        """Test setting project name"""
        set_project_name("Test Project")
        assert get_project_name() == "Test Project"


class TestParameters:
    """Test parameter getters and setters"""
    
    def setup_method(self):
        """Setup for each test"""
        MockStreamlit.session_state.clear()
        init_session_state()
    
    def test_get_parameters_default(self):
        """Test default parameters is empty dict"""
        assert get_parameters() == {}
    
    def test_set_parameters(self):
        """Test setting parameters"""
        params = {"threshold": 160, "kernel_size": 2}
        set_parameters(params)
        assert get_parameters() == params
    
    def test_set_parameters_overwrites(self):
        """Test that set_parameters overwrites previous values"""
        set_parameters({"threshold": 160})
        set_parameters({"kernel_size": 2})
        assert get_parameters() == {"kernel_size": 2}


class TestUploadedFiles:
    """Test uploaded files handling"""
    
    def setup_method(self):
        """Setup for each test"""
        MockStreamlit.session_state.clear()
        init_session_state()
    
    def test_get_uploaded_files_default(self):
        """Test default uploaded files is empty dict"""
        assert get_uploaded_files() == {}


class TestStateValidation:
    """Test state validation"""
    
    def setup_method(self):
        """Setup for each test"""
        MockStreamlit.session_state.clear()
        init_session_state()
    
    def test_validate_state_valid(self):
        """Test validation of valid state"""
        assert validate_state() is True
    
    def test_validate_state_invalid_workflow_step(self):
        """Test validation fails with invalid workflow step"""
        MockStreamlit.session_state["workflow_step"] = 10
        assert validate_state() is False
    
    def test_validate_state_invalid_parameters(self):
        """Test validation fails with invalid parameters"""
        MockStreamlit.session_state["parameters"] = "invalid"
        assert validate_state() is False


class TestStateReset:
    """Test state reset functionality"""
    
    def setup_method(self):
        """Setup for each test"""
        MockStreamlit.session_state.clear()
        init_session_state()
    
    def test_reset_session_state(self):
        """Test resetting entire session state"""
        set_workflow_step(5)
        set_project_name("Test")
        
        reset_session_state()
        
        assert get_workflow_step() == 0
        assert get_project_name() == ""


class TestWorkflowProgression:
    """Test workflow progression logic"""
    
    def setup_method(self):
        """Setup for each test"""
        MockStreamlit.session_state.clear()
        init_session_state()
    
    def test_can_proceed_from_home(self):
        """Test can proceed from home page"""
        set_workflow_step(0)
        assert can_proceed_to_next_step() is True
    
    def test_cannot_proceed_without_files(self):
        """Test cannot proceed from load data without files"""
        set_workflow_step(1)
        assert can_proceed_to_next_step() is False
    
    def test_can_proceed_with_files(self):
        """Test can proceed from load data with files"""
        set_workflow_step(1)
        MockStreamlit.session_state["uploaded_files"]["test.tif"] = "data"
        assert can_proceed_to_next_step() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

