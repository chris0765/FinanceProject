import pandas as pd
import numpy as np
import re
import os
from konlpy.tag import Okt
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
import pickle5 as pickle

okt = Okt()

PATH = os.getcwd() + os.path.sep
DATA_PATH = PATH+"data"+os.path.sep

newsData = pd.read_csv(DATA_PATH+"News_Info.csv", dtype={"단축코드":"object"})
priceData = pd.read_csv(DATA_PATH+"Price_Info.csv", dtype={"단축코드":"object"})

mergedData = pd.merge(newsData, priceData, how='inner', on=['단축코드', '한글 종목약명', '날짜'])

mergedData = mergedData[mergedData['내용'].notnull()]
# mergedData['내용'] = mergedData['내용'].apply(lambda x : re.sub(r'[^ ㄱ-ㅣ가-힣]+', " ", x))

text = mergedData['내용']
score = mergedData['상승/하락']

print("Prepare train&test dataset(8:2)")

train_x, test_x, train_y, test_y = train_test_split(text, score, test_size=0.2, random_state=0)

print("Vectorizer")

tfv_train_x = None
tfv = TfidfVectorizer(tokenizer=okt.morphs, ngram_range=(1,2), min_df=3, max_df=0.9)
tfv.fit(train_x)
tfv_train_x = tfv.transform(train_x)
pickle.dump(tfv_train_x, open("tfv_train_x.pkl", "wb"))

print(tfv_train_x)

print("Train...")

clf = LogisticRegression(random_state=0)
params = {'C': [15, 18, 19, 20, 22]}
grid_cv = GridSearchCV(clf, param_grid=params, cv=3, scoring='accuracy', verbose=1)
grid_cv.fit(tfv_train_x, train_y)

pickle.dump(grid_cv, open(PATH+"model/model.pkl", "wb"))

print("Train complete")
print(grid_cv.best_params_, grid_cv.best_score_)

print("Test...")
tfv_test_x = tfv.transform(test_x)
test_predict = grid_cv.best_estimator_.predict(tfv_test_x)

print("Test complete")
print(round(accuracy_score(test_y, test_predict), 3))

