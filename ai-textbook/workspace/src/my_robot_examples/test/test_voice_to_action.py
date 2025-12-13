#!/usr/bin/env python3
"""
Unit tests for the voice_to_action.py module
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the voice_control module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'my_robot_examples', 'voice_control'))

from voice_to_action import (
    SpeechRecognizer,
    NaturalLanguageProcessor,
    IsaacSimInterface,
    VoiceToActionSystem
)


class TestSpeechRecognizer(unittest.TestCase):
    """Test cases for SpeechRecognizer class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.recognizer = SpeechRecognizer()

    def test_initialization(self):
        """Test that SpeechRecognizer initializes correctly."""
        self.assertIsNotNone(self.recognizer)
        # Check that required attributes are initialized
        self.assertTrue(hasattr(self.recognizer, 'recognizer'))
        self.assertTrue(hasattr(self.recognizer, 'microphone'))

    @patch('voice_to_action.sr.Recognizer')
    def test_listen_with_adjust_for_ambient_noise(self, mock_recognizer_class):
        """Test that the recognizer adjusts for ambient noise."""
        # Mock the recognizer instance
        mock_recognizer_instance = Mock()
        mock_recognizer_class.return_value = mock_recognizer_instance

        # Create a new instance to use the mocked recognizer
        recognizer = SpeechRecognizer()

        # Check that adjust_for_ambient_noise was called during initialization
        mock_recognizer_instance.adjust_for_ambient_noise.assert_called_once()


class TestNaturalLanguageProcessor(unittest.TestCase):
    """Test cases for NaturalLanguageProcessor class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.nlp = NaturalLanguageProcessor()

    def test_initialization(self):
        """Test that NaturalLanguageProcessor initializes correctly."""
        self.assertIsNotNone(self.nlp)
        self.assertEqual(self.nlp.intent_patterns, {})

    def test_add_intent_pattern(self):
        """Test adding intent patterns."""
        self.nlp.add_intent_pattern('greet', ['hello', 'hi', 'hey'])
        self.assertIn('greet', self.nlp.intent_patterns)
        self.assertEqual(self.nlp.intent_patterns['greet'], ['hello', 'hi', 'hey'])

    def test_classify_intent(self):
        """Test intent classification."""
        self.nlp.add_intent_pattern('greet', ['hello', 'hi', 'hey'])
        self.nlp.add_intent_pattern('move', ['go', 'move', 'navigate'])

        intent = self.nlp.classify_intent('hello robot')
        self.assertEqual(intent, 'greet')

        intent = self.nlp.classify_intent('move forward')
        self.assertEqual(intent, 'move')

    def test_classify_intent_no_match(self):
        """Test intent classification with no match."""
        self.nlp.add_intent_pattern('greet', ['hello', 'hi', 'hey'])

        intent = self.nlp.classify_intent('unknown command')
        self.assertIsNone(intent)

    def test_extract_entities(self):
        """Test entity extraction."""
        # Test with a simple pattern
        text = "move robot to kitchen"
        entities = self.nlp.extract_entities(text, {'location': r'\b(kitchen|living room|bedroom)\b'})
        self.assertIn('kitchen', entities.values())


class TestIsaacSimInterface(unittest.TestCase):
    """Test cases for IsaacSimInterface class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.isaac_interface = IsaacSimInterface()

    def test_initialization(self):
        """Test that IsaacSimInterface initializes correctly."""
        self.assertIsNotNone(self.isaac_interface)


class TestVoiceToActionSystem(unittest.TestCase):
    """Test cases for VoiceToActionSystem class"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_isaac = Mock(spec=IsaacSimInterface)
        self.voice_system = VoiceToActionSystem(isaac_interface=self.mock_isaac)

    def test_initialization(self):
        """Test that VoiceToActionSystem initializes correctly."""
        self.assertIsNotNone(self.voice_system)
        self.assertIsNotNone(self.voice_system.speech_recognizer)
        self.assertIsNotNone(self.voice_system.nlp)
        self.assertIsNotNone(self.voice_system.isaac_interface)

    @patch('voice_to_action.SpeechRecognizer')
    def test_process_voice_command_success(self, mock_speech_recognizer_class):
        """Test processing a voice command successfully."""
        # Set up mocks
        mock_recognizer_instance = Mock()
        mock_recognizer_instance.recognize_with_context.return_value = "move to kitchen"
        mock_speech_recognizer_class.return_value = mock_recognizer_instance

        # Create a new instance with the mocked recognizer
        mock_isaac = Mock(spec=IsaacSimInterface)
        voice_system = VoiceToActionSystem(isaac_interface=mock_isaac)

        # Add intent pattern for testing
        voice_system.nlp.add_intent_pattern('move', [r'move to (\w+)'])

        # Process the command
        result = voice_system.process_voice_command()

        # Check that the command was processed
        self.assertIsNotNone(result)


def suite():
    """Create a test suite combining all test cases."""
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestSpeechRecognizer))
    suite.addTest(unittest.makeSuite(TestNaturalLanguageProcessor))
    suite.addTest(unittest.makeSuite(TestIsaacSimInterface))
    suite.addTest(unittest.makeSuite(TestVoiceToActionSystem))
    return suite


if __name__ == '__main__':
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())