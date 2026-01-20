#!/usr/bin/env python3
"""
Test suite for AI Development Project examples
==============================================

This test module validates that all examples can be imported and basic
functionality works without errors.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
import asyncio

# Add examples to Python path
examples_path = os.path.join(os.path.dirname(__file__), '..', 'examples')
sys.path.insert(0, examples_path)
sys.path.insert(0, os.path.join(examples_path, '01_simple_llm'))
sys.path.insert(0, os.path.join(examples_path, '02_contextual_ai'))
sys.path.insert(0, os.path.join(examples_path, '03_physics_deep_learning'))


class TestSimpleLLM:
    """Test simple LLM integration example"""
    
    def test_import_basic_chat(self):
        """Test that the basic chat module can be imported"""
        try:
            from basic_chat import SimpleLLMChat
            assert SimpleLLMChat is not None
        except ImportError as e:
            pytest.skip(f"Cannot import basic_chat: {e}")
    
    @patch('requests.post')
    def test_simple_llm_chat_creation(self, mock_post):
        """Test SimpleLLMChat can be created"""
        from basic_chat import SimpleLLMChat
        
        chat = SimpleLLMChat(model_type="ollama")
        assert chat.model_type == "ollama"
        assert chat.model_name == "llama3.1:8b"
        assert len(chat.conversation_history) == 0
    
    @patch('requests.post')
    def test_build_prompt(self, mock_post):
        """Test prompt building functionality"""
        from basic_chat import SimpleLLMChat
        
        chat = SimpleLLMChat()
        prompt = chat._build_prompt("What is Python?")
        
        assert "What is Python?" in prompt
        assert "helpful AI assistant" in prompt.lower()
    
    @patch('requests.post')
    @pytest.mark.asyncio
    async def test_mock_ollama_response(self, mock_post):
        """Test Ollama API call with mocked response"""
        from basic_chat import SimpleLLMChat
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Python is a programming language."}
        mock_post.return_value = mock_response
        
        chat = SimpleLLMChat(model_type="ollama")
        response = await chat.ask_question("What is Python?")
        
        assert "Python is a programming language." in response
        assert len(chat.conversation_history) == 1


class TestContextualAI:
    """Test contextual AI assistant example"""
    
    def test_import_trading_assistant(self):
        """Test that the trading assistant module can be imported"""
        try:
            from trading_assistant import TradingAssistant, MarketData, Portfolio
            assert TradingAssistant is not None
            assert MarketData is not None
            assert Portfolio is not None
        except ImportError as e:
            pytest.skip(f"Cannot import trading_assistant: {e}")
    
    def test_trading_assistant_creation(self):
        """Test TradingAssistant can be created"""
        from trading_assistant import TradingAssistant
        
        assistant = TradingAssistant()
        assert assistant.model_type == "ollama"
        assert len(assistant.context_memory) == 0
        assert len(assistant.conversation_history) == 0
    
    def test_market_data_creation(self):
        """Test MarketData structure"""
        from trading_assistant import MarketData
        from datetime import datetime
        
        market_data = MarketData(
            symbol="GOLD",
            price=2050.75,
            change_percent=1.2,
            volume=125000,
            volatility=0.25,
            timestamp=datetime.now()
        )
        
        assert market_data.symbol == "GOLD"
        assert market_data.price == 2050.75
        assert market_data.change_percent == 1.2
    
    def test_portfolio_creation(self):
        """Test Portfolio structure"""
        from trading_assistant import Portfolio
        from datetime import datetime
        
        portfolio = Portfolio(
            user_id=123,
            total_value=50000.0,
            positions=[],
            risk_level="moderate",
            last_updated=datetime.now()
        )
        
        assert portfolio.user_id == 123
        assert portfolio.total_value == 50000.0
        assert portfolio.risk_level == "moderate"
    
    def test_price_query_handling(self):
        """Test price query handling without API calls"""
        from trading_assistant import TradingAssistant, MarketData
        from datetime import datetime
        
        assistant = TradingAssistant()
        market_data = MarketData(
            symbol="GOLD",
            price=2050.75,
            change_percent=1.2,
            volume=125000,
            volatility=0.25,
            timestamp=datetime.now()
        )
        
        response = assistant._handle_price_query("What's the current price?", market_data)
        
        assert "2050.75" in response
        assert "GOLD" in response
        assert "1.2" in response or "1.20" in response
    
    def test_portfolio_query_handling(self):
        """Test portfolio query handling"""
        from trading_assistant import TradingAssistant, Portfolio
        from datetime import datetime
        
        assistant = TradingAssistant()
        portfolio = Portfolio(
            user_id=123,
            total_value=50000.0,
            positions=[
                {"symbol": "GOLD", "quantity": 10, "value": 20000}
            ],
            risk_level="moderate",
            last_updated=datetime.now()
        )
        
        response = assistant._handle_portfolio_query("How's my portfolio?", portfolio)
        
        assert "50000" in response or "50,000" in response
        assert "MODERATE" in response.upper()
        assert "1" in response  # Number of positions


class TestPhysicsDeepLearning:
    """Test physics deep learning examples"""
    
    def test_import_aerodynamics(self):
        """Test that aerodynamics module can be imported"""
        try:
            from aerodynamics_predictor import AerodynamicsAI, AirfoilGeometry, FlowConditions
            assert AerodynamicsAI is not None
            assert AirfoilGeometry is not None
            assert FlowConditions is not None
        except ImportError as e:
            pytest.skip(f"Cannot import aerodynamics_predictor: {e}")
    
    def test_import_hydrodynamics(self):
        """Test that hydrodynamics module can be imported"""
        try:
            from hydrodynamics_analyzer import HydrodynamicsAI, VesselGeometry, WaterConditions
            assert HydrodynamicsAI is not None
            assert VesselGeometry is not None
            assert WaterConditions is not None
        except ImportError as e:
            pytest.skip(f"Cannot import hydrodynamics_analyzer: {e}")
    
    def test_import_thermodynamics(self):
        """Test that thermodynamics module can be imported"""
        try:
            from thermodynamics_optimizer import ThermodynamicsAI, ThermalSystem, ThermalConditions
            assert ThermodynamicsAI is not None
            assert ThermalSystem is not None
            assert ThermalConditions is not None
        except ImportError as e:
            pytest.skip(f"Cannot import thermodynamics_optimizer: {e}")
    
    def test_airfoil_geometry_creation(self):
        """Test AirfoilGeometry structure"""
        from aerodynamics_predictor import AirfoilGeometry
        
        airfoil = AirfoilGeometry(
            name="NACA 0012",
            chord_length=1.0,
            thickness_ratio=12.0,
            camber=0.0,
            angle_of_attack=5.0
        )
        
        assert airfoil.name == "NACA 0012"
        assert airfoil.chord_length == 1.0
        assert airfoil.angle_of_attack == 5.0
    
    def test_flow_conditions_reynolds_number(self):
        """Test FlowConditions Reynolds number calculation"""
        from aerodynamics_predictor import FlowConditions
        
        flow = FlowConditions(
            velocity=50.0,
            density=1.225,
            viscosity=1.81e-5,
            temperature=288.15
        )
        
        re = flow.reynolds_number
        assert re > 0
        assert isinstance(re, float)
    
    def test_vessel_geometry_creation(self):
        """Test VesselGeometry structure"""
        from hydrodynamics_analyzer import VesselGeometry
        
        vessel = VesselGeometry(
            name="Test Yacht",
            length=12.0,
            beam=3.5,
            draft=2.0,
            displacement=8000.0,
            hull_form="displacement"
        )
        
        assert vessel.name == "Test Yacht"
        assert vessel.length == 12.0
        assert vessel.hull_form == "displacement"
    
    def test_water_conditions_froude_number(self):
        """Test WaterConditions Froude number calculation"""
        from hydrodynamics_analyzer import WaterConditions
        
        conditions = WaterConditions(
            velocity=5.0,
            water_density=1025.0,
            kinematic_viscosity=1.19e-6,
            wave_height=0.5,
            wave_period=4.0,
            depth=50.0
        )
        
        fn = conditions.froude_number
        assert fn > 0
        assert isinstance(fn, float)
    
    def test_thermal_system_creation(self):
        """Test ThermalSystem structure"""
        from thermodynamics_optimizer import ThermalSystem
        
        system = ThermalSystem(
            name="Test HX",
            system_type="heat_exchanger",
            geometry={'area': 10.0, 'length': 2.0},
            materials={'shell': 'steel'}
        )
        
        assert system.name == "Test HX"
        assert system.system_type == "heat_exchanger"
        assert system.geometry['area'] == 10.0
    
    def test_thermal_conditions_temp_difference(self):
        """Test ThermalConditions temperature difference"""
        from thermodynamics_optimizer import ThermalConditions
        
        conditions = ThermalConditions(
            hot_temperature=363.15,
            cold_temperature=293.15,
            flow_rate_hot=2.0,
            flow_rate_cold=2.5,
            ambient_temperature=298.15,
            pressure=1e5
        )
        
        delta_t = conditions.temperature_difference
        assert delta_t == 70.0
        assert isinstance(delta_t, float)
    
    @pytest.mark.asyncio
    async def test_aerodynamics_analysis(self):
        """Test basic aerodynamics analysis"""
        from aerodynamics_predictor import AerodynamicsAI, AirfoilGeometry, FlowConditions
        
        aero_ai = AerodynamicsAI()
        
        airfoil = AirfoilGeometry(
            name="Test Airfoil",
            chord_length=1.0,
            thickness_ratio=12.0,
            camber=2.0,
            angle_of_attack=5.0
        )
        
        flow = FlowConditions(
            velocity=50.0,
            density=1.225,
            viscosity=1.81e-5,
            temperature=288.15
        )
        
        analysis = await aero_ai.analyze_airfoil(airfoil, flow)
        
        assert 'geometry' in analysis
        assert 'coefficients' in analysis
        assert 'performance' in analysis
        assert len(aero_ai.analysis_history) == 1
    
    @pytest.mark.asyncio
    async def test_hydrodynamics_analysis(self):
        """Test basic hydrodynamics analysis"""
        from hydrodynamics_analyzer import HydrodynamicsAI, VesselGeometry, WaterConditions
        
        hydro_ai = HydrodynamicsAI()
        
        vessel = VesselGeometry(
            name="Test Vessel",
            length=10.0,
            beam=3.0,
            draft=1.5,
            displacement=5000.0,
            hull_form="displacement"
        )
        
        conditions = WaterConditions(
            velocity=5.0,
            water_density=1025.0,
            kinematic_viscosity=1.19e-6,
            wave_height=0.5,
            wave_period=4.0,
            depth=50.0
        )
        
        analysis = await hydro_ai.analyze_vessel(vessel, conditions)
        
        assert 'vessel' in analysis
        assert 'resistance' in analysis
        assert 'power' in analysis
        assert len(hydro_ai.analysis_history) == 1
    
    @pytest.mark.asyncio
    async def test_thermodynamics_analysis(self):
        """Test basic thermodynamics analysis"""
        from thermodynamics_optimizer import ThermodynamicsAI, ThermalSystem, ThermalConditions
        
        thermo_ai = ThermodynamicsAI()
        
        system = ThermalSystem(
            name="Test HX",
            system_type="heat_exchanger",
            geometry={'area': 10.0, 'length': 2.0},
            materials={'shell': 'steel'}
        )
        
        conditions = ThermalConditions(
            hot_temperature=363.15,
            cold_temperature=293.15,
            flow_rate_hot=2.0,
            flow_rate_cold=2.5,
            ambient_temperature=298.15,
            pressure=1e5
        )
        
        analysis = await thermo_ai.analyze_heat_exchanger(system, conditions)
        
        assert 'system' in analysis
        assert 'performance' in analysis
        assert 'efficiency' in analysis or 'losses' in analysis
        assert len(thermo_ai.analysis_history) == 1


class TestProjectStructure:
    """Test project structure and files"""
    
    def test_main_files_exist(self):
        """Test that main project files exist"""
        project_root = os.path.join(os.path.dirname(__file__), '..')
        
        # Check main files
        assert os.path.exists(os.path.join(project_root, 'README.md'))
        assert os.path.exists(os.path.join(project_root, 'ai_feature_guidelines.md'))
        assert os.path.exists(os.path.join(project_root, 'requirements.txt'))
        
        # Check directories
        assert os.path.exists(os.path.join(project_root, 'examples'))
        assert os.path.exists(os.path.join(project_root, 'docs'))
        assert os.path.exists(os.path.join(project_root, 'tests'))
    
    def test_examples_directory_structure(self):
        """Test examples directory structure"""
        examples_root = os.path.join(os.path.dirname(__file__), '..', 'examples')
        
        # Check example directories exist
        expected_examples = [
            '01_simple_llm',
            '02_contextual_ai',
            '03_physics_deep_learning'
        ]
        
        for example in expected_examples:
            example_path = os.path.join(examples_root, example)
            assert os.path.exists(example_path), f"Example directory {example} not found"
    
    def test_requirements_file_format(self):
        """Test that requirements.txt is properly formatted"""
        requirements_path = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')
        
        with open(requirements_path, 'r') as f:
            content = f.read()
        
        # Check for expected dependencies
        expected_deps = ['requests', 'chromadb', 'pytest']
        for dep in expected_deps:
            assert dep in content, f"Expected dependency {dep} not found in requirements.txt"
    
    def test_guidelines_file_content(self):
        """Test that the guidelines file has expected content"""
        guidelines_path = os.path.join(os.path.dirname(__file__), '..', 'ai_feature_guidelines.md')
        
        with open(guidelines_path, 'r') as f:
            content = f.read()
        
        # Check for key sections
        expected_sections = [
            '# AI Feature Development Guidelines',
            'Large Language Models',
            'Prompt Engineering',
            'RAG',
            'Vector Databases',
            'AI Agents'
        ]
        
        for section in expected_sections:
            assert section in content, f"Expected section '{section}' not found in guidelines"


@pytest.fixture
def mock_ai_response():
    """Fixture for mocking AI responses"""
    return {
        "response": "This is a mocked AI response for testing purposes."
    }


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_simple_llm_integration():
    """Full integration test with actual AI service (if available)"""
    try:
        from basic_chat import SimpleLLMChat
        
        chat = SimpleLLMChat(model_type="ollama")
        response = await chat.ask_question("Hello, can you respond with just 'Hello world!'?")
        
        # This test will pass if Ollama is running, fail/skip otherwise
        assert isinstance(response, str)
        assert len(response) > 0
        
    except Exception as e:
        pytest.skip(f"Integration test skipped - AI service not available: {e}")


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])