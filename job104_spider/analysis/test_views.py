from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, mock_open
from .test_jobs_om import ObjectMother
from django.core.paginator import Paginator
from itertools import cycle
import subprocess
import json

# Create your tests here.
class JobSearchTests(TestCase):
    def setUp(self):
        self.client = Client()

    @patch('builtins.open', new_callable=mock_open, read_data=json.dumps({
        'areas': [{'id': '6001001000', 'name': '台北市'}, {'id': '6001016000', 'name': '高雄市'}],
        'work_shifts': [{'id': '1', 'name': '日班'}, {'id': '2', 'name': '夜班'}],
        'company_types': [{'id': '16', 'name': '上市上櫃'}, {'id': '5', 'name': '外商一般'}],
        'benefits': [{'id': '1', 'name': '年終獎金'}, {'id': '2', 'name': '三節獎金'}]
    }))
    def test_index_view(self, mock_open):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Job Search')

        # Ensure the JSON data is being loaded correctly
        context = response.context
        self.assertIn('areas', context)
        self.assertIn('work_shifts', context)
        self.assertIn('company_types', context)
        self.assertIn('benefits', context)
        
        # Ensure the areas data from the mocked JSON is passed
        self.assertEqual(context['areas'][0]['name'], '台北市')

    @patch('analysis.job104_spider.Job104Spider.search')
    @patch('analysis.job104_spider.Job104Spider.search_job_transform')
    def test_search_view(self, mock_transform, mock_search):
        # Use ObjectMother to create the job data
        mock_search.return_value = (100, [ObjectMother.create_job_data() for _ in range(25)])  # 25 mock jobs
        mock_transform.side_effect = cycle([ObjectMother.create_transformed_data()])  # Infinite cycle

        # Mock the POST request with a keyword and check the search function
        response = self.client.post(reverse('search'), {'keyword': 'python'}, follow=True)

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
        self.assertEqual(session['total_count'], 100)

        # Ensure results are present (in this case, mock data will determine this)
        self.assertEqual(len(session['results']), 25)

        # Simulate a GET request for the second page
        response_page_2 = self.client.get(reverse('search') + '?page=2')

        # Check if the second page loads correctly
        self.assertEqual(response_page_2.status_code, 200)
        self.assertContains(response_page_2, 'Job Search')

        # Verify the pagination for the second page
        paginator = Paginator(session['results'], 20)  # Paginator set to 20 jobs per page
        page_obj = paginator.get_page(2)
        
        # Ensure we are on the second page and there are 20 jobs on this page
        self.assertEqual(page_obj.number, 2)
        self.assertEqual(len(page_obj.object_list), 5)

    @patch('analysis.job104_spider.Job104Spider.search')
    @patch('analysis.job104_spider.Job104Spider.search_job_transform')
    def test_pagination_does_not_retrigger_search(self, mock_transform, mock_search):
        # This test ensures pagination does not trigger another API call
        
        # Mock search results
        mock_search.return_value = (100, [ObjectMother.create_job_data() for _ in range(25)])
        mock_transform.side_effect = [ObjectMother.create_transformed_data() for _ in range(25)]

        # First, make a POST request to perform the initial search
        self.client.post(reverse('search'), {'keyword': 'python'}, follow=True)

        # Ensure the search was called once on the POST request
        self.assertEqual(mock_search.call_count, 1)

        # Now, simulate pagination (GET request to the second page)
        response_page_2 = self.client.get(reverse('search') + '?page=2')

        # Ensure search is not called again during pagination (no additional API call)
        self.assertEqual(mock_search.call_count, 1)  # Still 1, search should not be retriggered

        # Ensure the second page loads correctly with the paginated results
        self.assertEqual(response_page_2.status_code, 200)
        self.assertContains(response_page_2, 'Job Search')

class JobFitterTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Sample job data to store in session for the test
        self.sample_jobs = [
            {
                'name': 'Python Developer',
                'company_name': 'Tech Corp',
                'desc': 'Developing applications using Python and Django',
                'job_url': 'https://example.com/job/1'
            },
            {
                'name': 'Data Scientist',
                'company_name': 'Data Inc.',
                'desc': 'Analyzing data and building models using Python',
                'job_url': 'https://example.com/job/2'
            }
        ]

        self.sample_skills = "Python, Django, Data Science"

    @patch('subprocess.run')
    def test_run_job_fitter(self, mock_subprocess):
        print("test_run_job_fitter")
        # Mock the subprocess to return a successful result
        mock_subprocess.return_value = subprocess.CompletedProcess(
            args=['python', 'job_fitter_doc2vec.py'],
            returncode=0,
            stdout=json.dumps([{
                'name': 'Python Developer',
                'company_name': 'Tech Corp',
                'similarity_score': 0.95,
                'job_url': 'https://example.com/job/1'
            }]),
            stderr=''
        )

        # Set session data with job results (simulating a search that already occurred)
        session = self.client.session
        session['results'] = self.sample_jobs
        session.save()

        # Post the skills to run the job fitter
        response = self.client.post(reverse('run_job_fitter'), {'skills': self.sample_skills})

        # Check if the view returned a valid response
        self.assertEqual(response.status_code, 200)

        # Check if the session was updated with fitter results
        session = self.client.session
        self.assertIn('fitter_results', session)

        # Verify the fitter results
        fitter_results = session['fitter_results']
        self.assertEqual(fitter_results[0]['name'], 'Python Developer')
        self.assertEqual(fitter_results[0]['company_name'], 'Tech Corp')
        self.assertEqual(fitter_results[0]['similarity_score'], 0.95)