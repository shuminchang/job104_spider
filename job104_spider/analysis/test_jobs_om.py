class ObjectMother:
    @staticmethod
    def create_job_data():
        """Returns a sample job data dictionary as returned by the Job104Spider."""
        return {
            'jobType': 'Full-time',
            'jobName': 'Python Developer',
            'descSnippet': 'Developing web applications using Django and Python',
            'appearDate': '2024-09-11',
            'applyCnt': 5,
            'applyDesc': '5 applicants',
            'custName': 'Tech Corp',
            'jobAddrNoDesc': 'Taipei City',
            'jobAddress': 'Xinyi District',
            'link': {
                'job': '//www.104.com.tw/job/abcd1234',
                'cust': '//www.104.com.tw/company/abcd1234',
                'applyAnalyze': '//www.104.com.tw/jobs/apply/analysis/abcd1234'
            },
            'lon': 121.5654,
            'lat': 25.0330,
            'optionEdu': 'Bachelor’s degree',
            'periodDesc': '3-5 years',
            'salaryDesc': 'NT$50,000-70,000 per month',
            'salaryLow': 50000,
            'salaryHigh': 70000,
            'tags': ['Python', 'Django', 'Web Development']
        }
    
    @staticmethod
    def create_transformed_data():
        return {
            'job_id': 'abcd1234',
            'type': 'Full-time',
            'name': 'Python Developer',
            'desc': 'Developing web applications using Django and Python',
            'appear_date': '2024-09-11',
            'apply_num': 5,
            'apply_text': '5 applicants',
            'company_name': 'Tech Corp',
            'company_addr': 'Taipei City Xinyi District',
            'job_url': 'https://www.104.com.tw/job/abcd1234',
            'job_analyze_url': 'https://www.104.com.tw/apply/analysis/abcd1234',
            'job_company_url': 'https://www.104.com.tw/company/abcd1234',
            'lon': 121.5654,
            'lat': 25.0330,
            'education': 'Bachelor’s degree',
            'period': '3-5 years',
            'salary': 'NT$50,000-70,000 per month',
            'salary_high': 70000,
            'salary_low': 50000,
            'tags': ['Python', 'Django', 'Web Development'],
        }