from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from lightgbm import LGBMClassifier
import joblib
import numpy as np

class AzureCognitive:
    def __init__(self, ):
        self.model = joblib.load('model/model.pkl')
        self.key = '2b4b5aade54348d0918b20e39446f15e'
        self.endpoint = 'https://covidwizardta.cognitiveservices.azure.com/'

    def authenticate_client(self, ):
        ta_credential = AzureKeyCredential(self.key)
        text_analytics_client = TextAnalyticsClient(
                endpoint=self.endpoint, 
                credential=ta_credential)
        return text_analytics_client

    def health_extract(self, texts):
        documents = []
        documents.append(texts)
        client = self.authenticate_client()
        poller = client.begin_analyze_healthcare_entities(documents)
        result = poller.result()
        extracts=[]
        cat_ent={}
        docs = [doc for doc in result if not doc.is_error]

        for idx, doc in enumerate(docs):
            for entity in doc.entities:
                extracts.append(entity.normalized_text)
                try:
                    cat_ent[entity.category].append(entity.text)
                except:
                    cat_ent[entity.category] = [entity.text]

        return extracts, cat_ent

    def get_features(self, text):
        extracts, cat_ent = self.health_extract(text)
        X_test = [0]*8

        symptoms = ['Coughing', 'Fever', 'Sore Throat', 'out (of) breath', 'Headache']

        if symptoms[0] in extracts:
            X_test[0] = 1

        if symptoms[1] in extracts:
            X_test[1] = 1

        if symptoms[2] in extracts:
            X_test[2] = 1

        if (('Dyspnea' in extracts) or (symptoms[3] in extracts)):
            X_test[3] = 1
    
        if symptoms[4] in extracts:
            X_test[4] = 1
    
        if 'Age' in cat_ent.keys():
            if (int(cat_ent['Age'][0]) > 60):
                X_test[5] = 1

        if 'Gender' in cat_ent.keys():
            if ((cat_ent['Gender'][0]=='Female') or (cat_ent['Gender'][0]=='female')):
                X_test[6] = 1
            elif ((cat_ent['Gender'][0]=='Male') or (cat_ent['Gender'][0]=='male')):
                X_test[7] = 1

        return np.array(X_test).reshape(1, -1)

    def get_prediction(self, text):
        X_test = self.get_features(text)
        prediction = self.model.predict(X_test)[0]

        if prediction==1:
            return 'You should visit a doctor; Your description is matching with Coronavirus symptoms. If you can not reach a doctor now then please call Helpline number.'
        else:
            return 'My algorithm says that you are not infected. However, you should contact your doctor if the symptoms persists.'
