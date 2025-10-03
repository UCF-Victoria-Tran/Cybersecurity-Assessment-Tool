from django.http import HttpResponse
from django.test import TestCase
from unittest.mock import patch, MagicMock, mock_open

from api.services import generate_content_from_gemini

class GeminiContentGenerationTests(TestCase):
    """
    Tests for the generate_content_from_gemini function.
    Mocks the external Google Generative AI API, PIL, and file I/O.
    """

    # 'module_path.object_name'
    PATCH_GENAI = 'api.services.genai'
    PATCH_IMAGE = 'api.services.Image'

    def setUp(self):
        """Set up a standard mock response object for the Gemini API call."""
        self.mock_response_text = "This is the successful AI-generated response."
        
        # 1. Mock the response object
        self.mock_response = MagicMock()
        self.mock_response.text = self.mock_response_text

        # 2. Mock the GenerativeModel instance (what is returned by the constructor)
        self.mock_model_instance = MagicMock()
        self.mock_model_instance.generate_content.return_value = self.mock_response
        
        # 3. Mock the GenerativeModel class itself (the constructor that is called)
        self.mock_genai_model = MagicMock(return_value=self.mock_model_instance)

    @patch(PATCH_GENAI)
    def test_text_only_generation_success(self, mock_genai):
        """Tests successful generation with a text prompt and no context file."""
        # Set our mock for the GenerativeModel class
        mock_genai.GenerativeModel = self.mock_genai_model

        prompt = "Summarize the history of mock objects in Python."
        result = generate_content_from_gemini(prompt=prompt)

        # Assertions
        self.assertEqual(result, self.mock_response_text)
        
        # Check that the model was configured correctly
        self.mock_genai_model.assert_called_once_with(
            model_name='gemini-2.5-pro', 
            system_instruction=''
        )
        # Check the contents passed to generate_content
        self.mock_model_instance.generate_content.assert_called_once_with(
            contents=[prompt, '']
        )

    @patch(PATCH_GENAI)
    @patch(PATCH_IMAGE)
    def test_image_context_success(self, mock_image, mock_genai):
        """Tests successful generation when an image file path is provided."""
        mock_genai.GenerativeModel = self.mock_genai_model

        # Mock Image.open to return a mock image object
        mock_image_object = MagicMock(name="MockImageFile")
        mock_image.open.return_value = mock_image_object

        prompt = "What is in this image?"
        filepath = "/path/to/my_photo.jpg"
        
        result = generate_content_from_gemini(prompt=prompt, context_filepath=filepath)

        self.assertEqual(result, self.mock_response_text)
        mock_image.open.assert_called_once_with(filepath)
        
        # The mock image object should be passed as context
        self.mock_model_instance.generate_content.assert_called_once_with(
            contents=[prompt, mock_image_object]
        )

    @patch(PATCH_GENAI)
    @patch('api.services.open', new_callable=mock_open)
    def test_pdf_context_success(self, mock_file_open, mock_genai):
        """Tests successful generation when a PDF file path is provided."""
        mock_genai.GenerativeModel = self.mock_genai_model

        # Define mock PDF content
        pdf_content = b'%PDF-1.4\n... binary pdf data ...'
        # Configure the mock open to return the content when read() is called
        mock_file_open.return_value.read.return_value = pdf_content

        prompt = "Translate the first chapter of this PDF."
        filepath = "/path/to/research_paper.pdf"

        # Call the function being tested
        generate_content_from_gemini(prompt=prompt, context_filepath=filepath)

        # Check that the file was opened and closed
        mock_file_open.assert_called_once_with(filepath, 'rb')
        mock_file_open.return_value.close.assert_called_once()

        # Check the contents passed to generate_content
        # Access the keyword arguments dictionary (call_args[1])
        # and then the 'contents' key
        contents_list = self.mock_model_instance.generate_content.call_args[1]['contents']
        
        # The second item in contents must be a Django HttpResponse object
        self.assertIsInstance(contents_list[1], HttpResponse)
        
        # Check that the HttpResponse was constructed correctly
        django_response_context = contents_list[1]
        self.assertEqual(django_response_context.content, pdf_content)
        self.assertEqual(django_response_context['Content-Type'], 'application/pdf')

    @patch(PATCH_GENAI)
    def test_with_system_instruction(self, mock_genai):
        """Tests that the system instruction is correctly passed to the model constructor."""
        mock_genai.GenerativeModel = self.mock_genai_model

        system_instr = "You are a professional technical writer."
        prompt = "Write a user manual section."
        
        generate_content_from_gemini(prompt=prompt, system_instruction=system_instr)

        # Assert the GenerativeModel was initialized with the correct instruction
        self.mock_genai_model.assert_called_once_with(
            model_name='gemini-2.5-pro', 
            system_instruction=system_instr
        )

    @patch(PATCH_GENAI)
    def test_api_call_failure_handling(self, mock_genai):
        """Tests the error path when the Gemini API call throws an exception."""
        # Configure the mock generate_content to raise an exception
        expected_error = "400 Invalid Argument: Invalid prompt format"
        self.mock_model_instance.generate_content.side_effect = Exception(expected_error)
        mock_genai.GenerativeModel = self.mock_genai_model

        prompt = "Trigger failure."
        result = generate_content_from_gemini(prompt=prompt)

        # Assert the function returns the formatted error message
        self.assertIn("An error occurred during generation:", result)
        self.assertIn(expected_error, result)

    @patch(PATCH_IMAGE)
    @patch(PATCH_GENAI)
    def test_invalid_image_filepath_handling(self, mock_genai, mock_image):
        """
        Tests that a file opening error is handled gracefully and the API call
        proceeds without a context file.
        """
        mock_genai.GenerativeModel = self.mock_genai_model
        self.mock_model_instance.generate_content.return_value = self.mock_response
        mock_image.open.side_effect = FileNotFoundError("The image file was not found.")

        prompt = "Test image error."
        filepath = "/invalid/path/non_existent.jpg"
        
        # Call the function
        result = generate_content_from_gemini(prompt=prompt, context_filepath=filepath)

        # The function should return the mock success response
        self.assertEqual(result, self.mock_response_text)
        
        # Check that Image.open was called and failed as expected
        mock_image.open.assert_called_once_with(filepath)
        
        # The API call should have been made, but with an empty context file
        self.mock_model_instance.generate_content.assert_called_once_with(
            contents=[prompt, '']
        )