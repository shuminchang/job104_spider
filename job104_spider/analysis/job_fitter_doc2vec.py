import sys
import json
import pandas as pd
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from sklearn.metrics.pairwise import cosine_similarity
import jieba
import string
import io

# Ensure UTF-8 encoding is used
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def preprocess_text(text, stop_words):
    # Convert text to lowercase for English
    text = text.lower()
    # Remove punctuation and special characters for English
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Tokenize the text using jieba for Chinese
    tokens = jieba.lcut(text)
    # Remove stopwords
    tokens = [word for word in tokens if word not in stop_words and word.strip() != '']
    return tokens

def job_fitter(skills, data_path):
    try:
        # Load the current jobs data
        real_job_data = pd.read_json(data_path)

        # Extract relevant columns for analysis
        real_job_data_subset = real_job_data[['name', 'company_name', 'desc', 'job_url']]

        # Define stopwords
        english_stopwords = [
            'i', 'me', 'my', 'myself', 'we', 'our', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves',
            'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'they', 'them', 'their',
            'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was',
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and',
            'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
            'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off',
            'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any',
            'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than',
            'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now'
        ]

        chinese_stopwords = [
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这'
        ]

        stop_words = set(english_stopwords + chinese_stopwords)

        # Apply preprocessing to the job descriptions
        real_job_data_subset['tokens'] = real_job_data_subset['desc'].apply(lambda x: preprocess_text(x, stop_words))

        # Tag the documents
        tagged_docs = [TaggedDocument(words=row['tokens'], tags=[str(i)]) for i, row in real_job_data_subset.iterrows()]

        # Train Doc2Vec model
        model = Doc2Vec(tagged_docs, vector_size=50, window=2, min_count=1, workers=4)

        # Prepare user's skills
        your_skills_tokens = preprocess_text(skills, stop_words)

        # Infer vector for user's skills
        your_skills_vector = model.infer_vector(your_skills_tokens)

        # Calculate similarity for each job
        similarity_scores = []
        for i in range(len(real_job_data_subset)):
            job_vector = model.dv[str(i)]
            similarity = cosine_similarity([your_skills_vector], [job_vector])[0][0]
            similarity_scores.append(similarity)

        # print(similarity_scores)
        # Add similarity scores to the DataFrame
        real_job_data_subset['similarity_score'] = similarity_scores

        # Rank jobs by similarity score
        ranked_jobs = real_job_data_subset.sort_values(by='similarity_score', ascending=False)

        # Round similarity score explicitly
        ranked_jobs['similarity_score'] = ranked_jobs['similarity_score'].apply(lambda x: round(x, 4))
        # Return the top 10 job matches
        top_jobs = ranked_jobs.head(10).to_dict(orient='records')
        return top_jobs
    except Exception as e:
        return {'error': str(e)}

if __name__ == "__main__":
    skills = sys.argv[1]
    data_path = sys.argv[2]
    top_jobs = job_fitter(skills, data_path)
    print(json.dumps(top_jobs, ensure_ascii=False, indent=4))
