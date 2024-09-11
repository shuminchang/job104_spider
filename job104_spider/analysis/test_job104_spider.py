import unittest
from unittest.mock import patch, Mock
from .job104_spider import Job104Spider
from .test_jobs_om import ObjectMother

class Job104SpiderTests(unittest.TestCase):
    
    @patch('requests.get')  # Mock the requests.get method
    def test_search(self, mock_get):
        # Mocked response for the API call
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'totalCount': 10,
                'totalPage': 1,
                'list': [
                    ObjectMother.create_job_data()
                ]
            }
        }

        # Configure the mock to return the mocked response
        mock_get.return_value = mock_response

        # Call the search method
        spider = Job104Spider()
        total_count, jobs = spider.search('python', max_num=10)

        # Assert that the total count matches the mocked data
        self.assertEqual(total_count, 10)
        
        # Check the first job in the list
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]['jobName'], 'Python Developer')
        self.assertEqual(jobs[0]['custName'], 'Tech Corp')

    def test_search_job_transform(self):
        # Sample input data as returned from the 104 API
        job_data = ObjectMother.create_job_data()

        # Call the method to transform the job data
        spider = Job104Spider()
        transformed_job = spider.search_job_transform(job_data)

        # Assert the transformed data is as expected
        self.assertEqual(transformed_job['name'], 'Python Developer')
        self.assertEqual(transformed_job['company_name'], 'Tech Corp')
        self.assertEqual(transformed_job['salary'], 'NT$50,000-70,000 per month')
        self.assertEqual(transformed_job['job_url'], 'https://www.104.com.tw/job/abcd1234')
        self.assertEqual(transformed_job['job_company_url'], 'https://www.104.com.tw/company/abcd1234')
