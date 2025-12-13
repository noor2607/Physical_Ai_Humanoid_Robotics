# Capstone Project Integration Guide

## Overview

This guide provides detailed instructions for integrating all components developed in Module 4 to create the autonomous humanoid final project. The capstone project combines voice recognition, LLM integration, cognitive planning, and robot execution to create a conversational robot that can understand natural language commands and execute complex tasks.

## Project Architecture

### System Components
```
Voice Input → Speech Recognition → LLM Processing → Cognitive Planning → Action Execution
     ↑                                                                    ↓
     └─── Audio Feedback ←────────────────────────────────────────────────┘
```

### Integration Points
1. **Voice Interface**: Connects speech recognition with NLP processing
2. **LLM Interface**: Bridges natural language understanding and task planning
3. **Cognitive Planning**: Links high-level goals to executable actions
4. **Isaac Sim Interface**: Executes planned actions in simulation

## Integration Steps

### Step 1: System Initialization

First, initialize all system components:

```python
import asyncio
from voice_to_action import VoiceToActionSystem
from llm_integration import IsaacLLMInterface, LLMConfig, LLMProvider
from cognitive_planning import CognitivePlanner, IsaacSimActionExecutor
from isaac_integration import IsaacSimInterface

def initialize_capstone_system():
    # Initialize LLM configuration
    llm_config = LLMConfig(
        provider=LLMProvider.OPENAI,  # Or your preferred provider
        model_name="gpt-3.5-turbo",   # Or gpt-4 for better performance
        api_key="your-api-key-here",
        temperature=0.7,
        max_tokens=1000
    )

    # Initialize Isaac Sim interface
    isaac_interface = IsaacSimInterface()

    # Initialize action executor
    action_executor = IsaacSimActionExecutor()

    # Initialize cognitive planner
    cognitive_planner = CognitivePlanner(action_executor)

    # Initialize LLM interface
    llm_interface = IsaacLLMInterface(llm_config)

    # Initialize voice-to-action system
    voice_system = VoiceToActionSystem()

    # Connect components
    voice_system.nlp_processor = llm_interface.reasoning_engine
    cognitive_planner.action_executor = action_executor

    return {
        'voice_system': voice_system,
        'llm_interface': llm_interface,
        'cognitive_planner': cognitive_planner,
        'isaac_interface': isaac_interface
    }
```

### Step 2: Command Processing Pipeline

Create a unified command processing pipeline that integrates all components:

```python
class CapstoneSystem:
    def __init__(self):
        self.components = initialize_capstone_system()
        self.is_running = False

    async def process_command(self, command_text: str):
        """
        Process a command through the full pipeline:
        Voice → NLP → LLM → Planning → Execution
        """
        try:
            # Step 1: Process with LLM for understanding and planning
            print(f"Processing command: {command_text}")

            # Get current world state from Isaac Sim
            robot_state = self.components['isaac_interface'].get_robot_state()
            env_state = self.components['isaac_interface'].get_environment_state()

            # Process command with LLM integration
            llm_response = await self.components['llm_interface'].reasoning_engine.process_natural_command(
                command_text, robot_state, env_state
            )

            if not llm_response.success:
                error_msg = f"LLM processing failed: {llm_response.content}"
                print(error_msg)
                await self._speak_response(error_msg)
                return False

            # Handle ambiguity
            if llm_response.clarification_needed and llm_response.clarification_question:
                print(f"Clarification needed: {llm_response.clarification_question}")
                await self._speak_response(llm_response.clarification_question)
                return False  # Need user clarification

            # Step 2: Execute the planned actions
            if llm_response.execution_plan:
                print(f"Executing plan with {len(llm_response.execution_plan)} steps")

                execution_results = []
                for i, action_step in enumerate(llm_response.execution_plan):
                    print(f"Step {i+1}/{len(llm_response.execution_plan)}: {action_step}")

                    # Execute action through Isaac Sim
                    result = await self.components['isaac_interface'].execute_action(
                        action_step["action"],
                        action_step.get("parameters", {})
                    )
                    execution_results.append(result)

                    if not result.get("success", False):
                        error_msg = f"Action failed at step {i+1}: {result.get('details', 'Unknown error')}"
                        print(error_msg)
                        await self._speak_response(error_msg)
                        return False

                # Step 3: Generate response to user
                response_text = await self.components['llm_interface'].reasoning_engine.generate_robot_response(
                    command_text, execution_results
                )

                print(f"Execution completed. Response: {response_text}")
                await self._speak_response(response_text)

                return True
            else:
                error_msg = "No execution plan generated"
                print(error_msg)
                await self._speak_response(error_msg)
                return False

        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            print(error_msg)
            await self._speak_response(error_msg)
            return False

    async def _speak_response(self, text: str):
        """Generate audio response to user (implementation depends on your audio system)"""
        # In Isaac Sim, you might use text-to-speech
        print(f"Robot says: {text}")
        # Add actual TTS implementation here

    def run_continuous(self):
        """Run the system in continuous listening mode"""
        self.is_running = True
        print("Starting continuous mode. Say 'stop' to end.")

        async def continuous_loop():
            while self.is_running:
                try:
                    # Listen for command
                    command = self.components['voice_system'].speech_recognizer.listen_once(timeout=5)
                    if command:
                        if 'stop' in command.lower():
                            print("Stop command detected. Ending continuous mode.")
                            self.is_running = False
                            await self._speak_response("Stopping. Goodbye!")
                            break

                        # Process the command
                        success = await self.process_command(command)
                        if not success:
                            await self._speak_response("I couldn't complete that task. Please try again.")

                except KeyboardInterrupt:
                    print("Interrupted by user")
                    self.is_running = False
                    break
                except Exception as e:
                    print(f"Error in continuous loop: {e}")
                    await self._speak_response("I encountered an error. Please wait.")
                    await asyncio.sleep(1)  # Brief pause before continuing

        # Run the event loop
        asyncio.run(continuous_loop())
```

### Step 3: Isaac Sim Integration

Connect your system to Isaac Sim properly:

```python
class IsaacSimConnector:
    def __init__(self):
        # Initialize connection to Isaac Sim
        # This would use Isaac Sim's Python API
        self.isaac_app = None
        self.robot = None
        self.scene = None

    def initialize_isaac(self):
        """Initialize Isaac Sim environment"""
        # Import Isaac Sim modules
        try:
            import omni
            import carb
            from omni.isaac.core import World
            from omni.isaac.core.utils.stage import add_reference_to_stage
            from omni.isaac.core.utils.nucleus import get_assets_root_path

            # Create world instance
            self.world = World(stage_units_in_meters=1.0)

            # Load robot and scene
            assets_root_path = get_assets_root_path()
            if assets_root_path is None:
                carb.log_error("Could not find Isaac Sim assets path")
                return False

            # Add your robot and scene here
            # Example: add_reference_to_stage(..., "/path/to/robot.usd")

            return True

        except ImportError:
            print("Isaac Sim modules not available - running in simulation mode")
            return False

    async def execute_action_in_isaac(self, action_type: str, parameters: dict):
        """Execute an action in Isaac Sim"""
        if not self.world:
            # Simulation mode - just return success
            await asyncio.sleep(parameters.get('duration', 1.0))
            return {"success": True, "message": f"Simulated {action_type}"}

        # Execute actual Isaac Sim action
        if action_type == "navigate":
            return await self._navigate_to_location(parameters.get('location'))
        elif action_type == "grasp":
            return await self._grasp_object(parameters.get('object'))
        elif action_type == "place":
            return await self._place_object(parameters.get('object'), parameters.get('location'))
        else:
            return {"success": False, "message": f"Unknown action: {action_type}"}

    async def _navigate_to_location(self, location: str):
        """Navigate robot to specified location in Isaac Sim"""
        # Implementation would use Isaac Sim navigation stack
        # This is a placeholder
        await asyncio.sleep(2)  # Simulate navigation time
        return {"success": True, "message": f"Navigated to {location}"}

    async def _grasp_object(self, obj_name: str):
        """Grasp object in Isaac Sim"""
        # Implementation would use Isaac Sim manipulation stack
        await asyncio.sleep(1.5)  # Simulate grasping time
        return {"success": True, "message": f"Grasped {obj_name}"}

    async def _place_object(self, obj_name: str, location: str):
        """Place object at location in Isaac Sim"""
        # Implementation would use Isaac Sim manipulation stack
        await asyncio.sleep(1.5)  # Simulate placement time
        return {"success": True, "message": f"Placed {obj_name} at {location}"}
```

## Complete Integration Example

Here's a complete example of how to tie everything together:

```python
async def main_capstone_demo():
    """Complete capstone project demonstration"""
    print("=== Autonomous Humanoid Robot Capstone Project ===")

    # Initialize all system components
    capstone_system = CapstoneSystem()

    # Example commands to demonstrate the system
    demo_commands = [
        "Go to the kitchen",
        "Find the red ball",
        "Pick up the red ball",
        "Place the red ball on the table",
        "Bring me the blue box from the living room"
    ]

    print("\nDemonstrating system with example commands...")

    for command in demo_commands:
        print(f"\nProcessing: '{command}'")
        success = await capstone_system.process_command(command)
        print(f"Result: {'Success' if success else 'Failed'}")
        await asyncio.sleep(2)  # Pause between commands

    print("\n=== Capstone System Ready for User Interaction ===")
    print("Starting continuous mode...")
    capstone_system.run_continuous()

if __name__ == "__main__":
    asyncio.run(main_capstone_demo())
```

## Testing and Validation

### Unit Testing Integration

Create tests to validate the integration:

```python
import unittest
from unittest.mock import Mock, AsyncMock

class TestCapstoneIntegration(unittest.TestCase):
    def setUp(self):
        # Mock the components for testing
        self.mock_isaac = Mock()
        self.mock_llm = Mock()
        self.mock_planner = Mock()

    async def test_command_processing_pipeline(self):
        """Test the complete command processing pipeline"""
        # Setup mock responses
        self.mock_llm.process_natural_command = AsyncMock(return_value=Mock(
            success=True,
            execution_plan=[
                {"action": "navigate", "parameters": {"location": "kitchen"}},
                {"action": "find", "parameters": {"object": "ball"}}
            ],
            clarification_needed=False
        ))

        # Test the pipeline
        capstone = CapstoneSystem()
        capstone.components['llm_interface'].reasoning_engine = self.mock_llm

        result = await capstone.process_command("Go to kitchen and find the ball")
        self.assertTrue(result)

    async def test_ambiguous_command_handling(self):
        """Test handling of ambiguous commands"""
        self.mock_llm.process_natural_command = AsyncMock(return_value=Mock(
            success=True,
            clarification_needed=True,
            clarification_question="Which ball do you mean?"
        ))

        capstone = CapstoneSystem()
        capstone.components['llm_interface'].reasoning_engine = self.mock_llm

        result = await capstone.process_command("Get the ball")
        self.assertFalse(result)  # Should return False due to clarification needed

# Run tests
if __name__ == "__main__":
    unittest.main()
```

## Performance Optimization

### Caching and Efficiency

```python
from functools import lru_cache
import asyncio
from typing import Dict, Any

class OptimizedCapstoneSystem(CapstoneSystem):
    def __init__(self):
        super().__init__()
        self._action_cache = {}
        self._command_cache = {}

    @lru_cache(maxsize=128)
    def _cached_plan_generation(self, goal: str, context: str) -> Any:
        """Cache plan generation for repeated goals"""
        # Implementation would call LLM with caching
        pass

    async def _execute_with_retry(self, action, max_retries=3):
        """Execute action with retry logic"""
        for attempt in range(max_retries):
            try:
                result = await self.components['isaac_interface'].execute_action(
                    action["action"],
                    action.get("parameters", {})
                )
                if result.get("success", False):
                    return result
                print(f"Attempt {attempt + 1} failed: {result.get('details', 'Unknown error')}")
            except Exception as e:
                print(f"Attempt {attempt + 1} error: {e}")

            if attempt < max_retries - 1:
                await asyncio.sleep(0.5 * (attempt + 1))  # Exponential backoff

        return {"success": False, "message": f"Failed after {max_retries} attempts"}
```

## Error Handling and Recovery

### Robust Error Handling

```python
class ResilientCapstoneSystem(CapstoneSystem):
    def __init__(self):
        super().__init__()
        self.error_history = []
        self.recovery_strategies = [
            self._retry_strategy,
            self._simplification_strategy,
            self._alternative_strategy
        ]

    async def process_command_with_recovery(self, command_text: str):
        """Process command with automatic error recovery"""
        try:
            return await self.process_command(command_text)
        except Exception as e:
            print(f"Command failed: {e}")
            self.error_history.append({
                "command": command_text,
                "error": str(e),
                "timestamp": time.time()
            })

            # Try recovery strategies
            for strategy in self.recovery_strategies:
                try:
                    result = await strategy(command_text, e)
                    if result is not None:
                        return result
                except Exception as recovery_error:
                    print(f"Recovery strategy failed: {recovery_error}")
                    continue

            # If all recovery strategies fail
            await self._speak_response("I'm having trouble with that command. Could you please rephrase it?")
            return False

    async def _retry_strategy(self, original_command: str, error: Exception):
        """Simple retry strategy"""
        print("Retrying command...")
        await asyncio.sleep(1)
        return await self.process_command(original_command)

    async def _simplification_strategy(self, original_command: str, error: Exception):
        """Try to simplify the command"""
        # Try to break down complex commands
        if "and" in original_command.lower():
            parts = original_command.lower().split("and")
            if len(parts) > 1:
                print("Simplifying command...")
                # Process first part only
                simplified = parts[0].strip()
                return await self.process_command(simplified)
        return None

    async def _alternative_strategy(self, original_command: str, error: Exception):
        """Try alternative approach"""
        # Ask for clarification or alternative
        await self._speak_response("I didn't understand that. Could you please rephrase your request?")
        return None
```

## Deployment Configuration

### Configuration File

Create a `config.yaml` for easy deployment:

```yaml
# Capstone Project Configuration
system:
  debug_mode: false
  log_level: "INFO"

llm:
  provider: "openai"
  model: "gpt-3.5-turbo"
  temperature: 0.7
  max_tokens: 1000
  timeout: 30

isaac_sim:
  enable_physics: true
  simulation_frequency: 60
  rendering: true

voice:
  sensitivity: 0.5
  language: "en-US"
  wake_word: "robot"

safety:
  max_navigation_time: 60
  battery_threshold: 15
  emergency_stop: true

performance:
  action_timeout: 10
  plan_timeout: 30
  response_timeout: 5
```

### Loading Configuration

```python
import yaml

def load_capstone_config(config_path: str = "config.yaml"):
    """Load configuration from YAML file"""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"Config file {config_path} not found. Using defaults.")
        return get_default_config()

def get_default_config():
    """Get default configuration"""
    return {
        "system": {
            "debug_mode": False,
            "log_level": "INFO"
        },
        "llm": {
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 1000
        },
        # ... other defaults
    }
```

## Final Integration Checklist

Before finalizing your capstone project, ensure all components are properly integrated:

- [ ] Voice recognition connects to NLP processing
- [ ] LLM integration handles command interpretation
- [ ] Cognitive planning generates executable actions
- [ ] Isaac Sim interface executes actions properly
- [ ] Error handling and recovery mechanisms work
- [ ] Performance is acceptable for real-time operation
- [ ] Safety constraints are enforced
- [ ] User feedback system is functional
- [ ] All components work together seamlessly

## Troubleshooting Common Issues

### 1. LLM Response Parsing Issues
- Ensure JSON responses are properly formatted
- Add error handling for malformed responses
- Implement fallback parsing strategies

### 2. Isaac Sim Connection Problems
- Verify Isaac Sim is properly installed and running
- Check that all required USD files are accessible
- Ensure proper permissions for Isaac Sim execution

### 3. Performance Bottlenecks
- Cache frequently used plans and responses
- Optimize LLM calls to reduce latency
- Use appropriate model sizes for your hardware

### 4. Ambiguous Command Handling
- Implement clear clarification strategies
- Provide helpful prompts to users
- Maintain context across interactions

## Conclusion

This integration guide provides the framework for connecting all components of your conversational robotics system. The capstone project demonstrates the full pipeline from natural language understanding to physical action execution in Isaac Sim. Focus on creating robust error handling, efficient performance, and natural user interaction for the best results.