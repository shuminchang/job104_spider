from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from .test_jobs_om import ObjectMother

# Create your tests here.
class JobSearchTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Job Search')

    @patch('analysis.job104_spider.Job104Spider.search')
    @patch('analysis.job104_spider.Job104Spider.search_job_transform')
    def test_search_view(self, mock_transform, mock_search):
        # Use ObjectMother to create the job data
        mock_search.return_value = (10, [ObjectMother.create_job_data()])
        mock_transform.return_value = ObjectMother.create_transformed_data()
        # Mock the POST request with a keyword and check the search function
        response = self.client.post(reverse('search'), {'keyword': 'python'})

        # Check if the response status code is 200
        self.assertEqual(response.status_code, 200)

        # Verify that session has been updated with search results
        session = self.client.session
        self.assertIn('results', session)
        self.assertIn('total_count', session)
        self.assertIn('keyword', session)

        # Ensure the keyword is stored correctly in the session
        self.assertEqual(session['keyword'], 'python')

        # Check if the total count is greater than or equal to 0
        self.assertEqual(session['total_count'], 10)

        # Ensure results are present (in this case, mock data will determine this)
        self.assertEqual(len(session['results']), 1)

        self.assertEqual(session['results'][0]['name'], 'Python Developer')