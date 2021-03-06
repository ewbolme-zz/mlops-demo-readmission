import pickle
import os
import pandas as pd
import numpy as np
from typing import List, Optional
from catboost import CatBoostClassifier
import io

def read_input_data(input_binary_data):
    return pd.read_csv(io.BytesIO(input_binary_data))

def fit(
    X: pd.DataFrame,
    y: pd.Series,
    output_dir: str,
    class_order: Optional[List[str]] = None,
    row_weights: Optional[np.ndarray] = None,
    **kwargs,
) -> None:

    #Take advantage of transform function below - This might not be applicable to your use case, depending on the preprocessing you do.
    X = transform(X,model=None)

    estimator = CatBoostClassifier(iterations=2,
                               depth=2,
                               learning_rate=1,
                               loss_function='Logloss',
                               verbose=True)

    cat_features = list(X.select_dtypes(include=object).columns)

    # train the model
    estimator.fit(X,y,cat_features)
    
    #Dumping the model in output_dir --> DataRobot will automatically find pkl files saved there.
    pickle.dump(estimator, open('{}/model.pkl'.format(output_dir), 'wb'))


def transform(data,model):
    """
    Note: This hook may not have to be implemented for your model.
    In this case implemented for the model used in the example.
    Modify this method to add data transformation before scoring calls. For example, this can be
    used to implement one-hot encoding for models that don't include it on their own.
    Parameters
    ----------
    data: pd.DataFrame
    model: object, the deserialized model
    Returns
    -------
    pd.DataFrame
    """
    # Execute any steps you need to do before scoring

    def find_diabetes_text(txt):
        try:
            if 'diabetes' in txt.lower():
                return 1
            else:
                return 0
        except:
            0
       
    #DataRobot Drum will check what happens when values are imputed. That is why I explicetely define cat_features
    cat_features = ['A1Cresult',
                    'acarbose',
                    'acetohexamide',
                    'admission_source_id',
                    'admission_type_id',
                    'age',
                    'change',
                    'chlorpropamide',
                    'citoglipton',
                    'diabetesMed',
                    'diag_1',
                    'diag_2',
                    'diag_3',
                    'discharge_disposition_id',
                    'examide',
                    'gender',
                    'glimepiride',
                    'glimepiride_pioglitazone',
                    'glipizide',
                    'glipizide_metformin',
                    'glyburide',
                    'glyburide_metformin',
                    'insulin',
                    'max_glu_serum',
                    'medical_specialty',
                    'metformin',
                    'metformin_pioglitazone',
                    'metformin_rosiglitazone',
                    'miglitol',
                    'nateglinide',
                    'payer_code',
                    'pioglitazone',
                    'race',
                    'repaglinide',
                    'rosiglitazone',
                    'tolazamide',
                    'tolbutamide',
                    'troglitazone',
                    'weight']

    # Fill null values for Categorical Features
    for c in cat_features:
        data[c] = data[c].fillna('unknown')

        #Some categorical features (diag_1), have float values which in reality are categories. Catboost takes either int or object as input
        #so I am casting.
        #try:
        #    data[c] = data[c].astype(int)
        #except:
            #pass

    # Find out if `Diabetes|`diabetes` exists in diag_1_desc column
    data['diabetes'] = data['diag_1_desc'].apply(lambda x: find_diabetes_text(x))
    data.drop(["diag_1_desc"], inplace=True, axis=1)    

    # Fill null values for numeric features
    data = data.fillna(0)

    return data

def score(data, model, **kwargs):

    results = model.predict_proba(data)

    #Create two columns with probability results
    predictions = pd.DataFrame({'True': results[:, 0]})
    predictions['False'] = 1 - predictions['True']

    return predictions