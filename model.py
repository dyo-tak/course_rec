import pandas as pd 
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity,linear_kernel
import json
from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return 'Hello, this is the Udemy Course Recommendation API!'

@app.route('/predict_course', methods=['GET'])
def predict_course():
    search_term = request.args.get('search_term')
    df = pd.read_csv("udemy_course_data.csv")
    cosine_sim_mat = vectorize_text_to_cosine_mat(df['course_title'])
    num_of_rec = 7
    if search_term is not None:
        try:
            results = get_recommendation(search_term, cosine_sim_mat, df, num_of_rec)
            jresult = pd.DataFrame(results)
            jresult = jresult.to_json(orient='records')
            return jresult
        except:
            results="Not Found"
            result_df=search_term_if_not_found(search_term, df)
            jresultx=pd.DataFrame(result_df)
            jresultx=jresultx.to_json(orient='records')
            return jresultx
    else:
        return 'Please provide a search term'

def load_data(data):
    df = pd.read_csv(data)
    return df

def vectorize_text_to_cosine_mat(data):
    count_vect = CountVectorizer()
    cv_mat = count_vect.fit_transform(data)
    cosine_sim_mat = cosine_similarity(cv_mat)
    return cosine_sim_mat

def get_recommendation(title,cosine_sim_mat,df,num_of_rec=10):
    course_indices = pd.Series(df.index,index=df['course_title']).drop_duplicates()
    idx = course_indices[title]
    sim_scores =list(enumerate(cosine_sim_mat[idx]))
    sim_scores = sorted(sim_scores,key=lambda x: x[1],reverse=True)
    selected_course_indices = [i[0] for i in sim_scores[1:]]
    selected_course_scores = [i[0] for i in sim_scores[1:]]
    result_df = df.iloc[selected_course_indices]
    result_df['similarity_score'] = selected_course_scores
    final_recommended_courses = result_df[['course_title','similarity_score','url','price','num_subscribers']]
    return final_recommended_courses.head(num_of_rec)

def search_term_if_not_found(term,df):
    result_df = df[df['course_title'].str.contains(term)]
    return result_df

if __name__ == '__main__':
    app.run(debug=True)
