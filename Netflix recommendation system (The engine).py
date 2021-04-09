from sklearn.feature_extraction.text import TfidfVectorizer 


tfidf = TfidfVectorizer(stop_words='english')
data['category'].replace('missing', '', inplace=True)

def gather(x) :
    return x['title'] + '' + x['country'] + '' + x['director'] + '' + x['listed_in'] + '' + x['description'] + '' + x['category']

# Constructing the required TF-IDF matrix by fitting and transforming the data
tfidf_matrix = tfidf.fit_transform(data.fillna('').apply(gather, axis=1))
tfidf_matrix.shape #(7787, 34767)

# We will be using the Cosine similarity metric
# This kernel is a popular choice for computing the similarity of documents represented as tf-idf vectors
# Since our vectors are already nomalized, cosine_similarity is equivalent to linear_kernel, which we will use instead

# Import linear_kernel
from sklearn.metrics.pairwise import linear_kernel

# Compute the linear similarity matrix
line_sim = linear_kernel(tfidf_matrix, tfidf_matrix) #(7787, 7787)

indices = pd.Series(data.index, index=data['title'])
def get_recommendations(title, sim=line_sim, n=10):
    idx = indices[title]

    # Get the similarity scores of all Movies/TV Shows with that Movie/TV Show and sort them
    similarity_scores = list(enumerate(sim[idx]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the n most similar Movies/TV Shows and their indices
    similarity_scores = similarity_scores[1:(n+1)]
    movie_indices = [i[0] for i in similarity_scores]

    # Return the top n most similar Movies/TV Shows
    return data['title'].iloc[movie_indices]

# Example :
get_recommendations('Sex Education')

#output :
#7473                      Wanderlust
#1640                  Dawson's Creek
#2806                        Hormones
#7655              Women Of The Night
#5525                  Sex, Explained
#1315                     Chewing Gum
#5226                       Riverdale
#5862                   Stunt Science
#690                    Bad Education
#6330    The End of the F***ing World
#Name: title, dtype: object
