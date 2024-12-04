import unittest
from unittest.mock import MagicMock, patch
from amazon_shopping_agent import AmazonShoppingAgent

class TestAmazonShoppingAgent(unittest.TestCase):
    @patch("amazon_shopping_agent.MemoryClient")
    @patch("amazon_shopping_agent.MultiOn")
    def test_ask_question(self, mock_multion, mock_memory_client):
        # Mock memory client behavior
        mock_memory = mock_memory_client.return_value
        mock_memory.search.return_value = [{"memory": "I like wireless headphones"}]
        
        # Mock MultiOn behavior
        mock_multion_instance = mock_multion.return_value
        mock_multion_instance.sessions.create.return_value.session_id = "test_session_id"
        mock_multion_instance.sessions.step.return_value = MagicMock(
            message="Here are the best wireless headphones.",
            status="SUCCESS",
            screenshot="http://example.com/screenshot.png"
        )
        
        # Initialize agent
        agent = AmazonShoppingAgent()
        
        # Test ask_question method
        question = "What are the best deals on wireless headphones?"
        user_id = "test_user"
        message, status = agent.ask_question(question, user_id)
        
        # Assertions
        self.assertEqual(message, "Here are the best wireless headphones.")
        self.assertEqual(status, "SUCCESS")
        mock_memory.search.assert_called_once_with(question, user_id="test_user")
        mock_multion_instance.sessions.step.assert_called_once()

    def test_create_prompt_no_memories(self):
        # Test _create_prompt with no relevant memories
        agent = AmazonShoppingAgent(use_memory=False)
        question = "What are the best deals on wireless headphones?"
        prompt = agent._create_prompt(question, relevant_memories="")
        
        expected_prompt = (
            "Perform action related to the user query and preferences for shopping on Amazon.com.\n"
            "Question: What are the best deals on wireless headphones?"
        )
        self.assertEqual(prompt, expected_prompt)

    def test_create_prompt_with_memories(self):
        # Test _create_prompt with relevant memories
        agent = AmazonShoppingAgent(use_memory=True)
        question = "What are the best deals on wireless headphones?"
        relevant_memories = "I like wireless headphones"
        prompt = agent._create_prompt(question, relevant_memories)
        
        expected_prompt = (
            "Perform action related to the user query and preferences for shopping on Amazon.com.\n"
            "Question: What are the best deals on wireless headphones?\n"
            "My preferences: I like wireless headphones"
        )
        self.assertEqual(prompt, expected_prompt)

if __name__ == "__main__":
    unittest.main()
