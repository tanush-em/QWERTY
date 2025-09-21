import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from aif360.datasets import BinaryLabelDataset
from aif360.algorithms.preprocessing import Reweighing
from aif360.metrics import BinaryLabelDatasetMetric
import numpy as np
np.random.seed(42)
n_samples = 200
age = np.random.randint(20, 80, n_samples)
gender = np.random.randint(0, 2, n_samples)
condition_score = np.random.rand(n_samples) * 10
labels = (condition_score + (gender * 0.5) + (age/100) > 8).astype(int)
df = pd.DataFrame({'age': age, 'gender': gender, 'condition_score': condition_score, 'label': labels})
dataset = BinaryLabelDataset(df=df,label_names=['label'], protected_attribute_names=['gender'])
train, test = dataset.split([0.7], shuffle=True, seed=42)
model_orig = RandomForestClassifier(random_state=42)
model_orig.fit(train.features, train.labels.ravel())
pred_orig = model_orig.predict(test.features)
test_pred_orig = test.copy()
test_pred_orig.labels = pred_orig.reshape(-1, 1)
metric_orig = BinaryLabelDatasetMetric(test_pred_orig, privileged_groups=[{'gender': 1}], unprivileged_groups=[{'gender': 0}])
print("Original Model Bias (Disparate Impact):", metric_orig.disparate_impact())
rew = Reweighing(unprivileged_groups=[{'gender': 0 }], privileged_groups=[{'gender': 1}])
train_rw = rew.fit_transform(train)
model_rw = RandomForestClassifier(random_state=42)
model_rw.fit(train_rw.features, train_rw.labels.ravel())
pred_rw = model_rw.predict(test.features)
test_pred_rw = test.copy()
test_pred_rw.labels = pred_rw.reshape(-1, 1)
metric_rw = BinaryLabelDatasetMetric(test_pred_rw, privileged_groups=[{'gender': 1}], unprivileged_groups=[{'gender': 0}])
print("Model After Reweighing Bias (Disparate Impact):", metric_rw.disparate_impact())

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from aif360.datasets import BinaryLabelDataset
from aif360.algorithms.preprocessing import Reweighing
from aif360.metrics import BinaryLabelDatasetMetric
import numpy as np
np.random.seed(42)
n_samples = 200
age = np.random.randint(20, 80, n_samples)
gender = np.random.randint(0, 2, n_samples)
condition_score = np.random.rand(n_samples) * 10
labels = (condition_score + (gender * 0.5) + (age/100) > 8).astype(int)
df = pd.DataFrame({'age': age, 'gender': gender, 'condition_score': condition_score, 'label': labels})
dataset = BinaryLabelDataset(df=df,label_names=['label'], protected_attribute_names=['gender'])
train, test = dataset.split([0.7], shuffle=True, seed=42)
model_orig = RandomForestClassifier(random_state=42)
model_orig.fit(train.features, train.labels.ravel())
pred_orig = model_orig.predict(test.features)
test_pred_orig = test.copy()
test_pred_orig.labels = pred_orig.reshape(-1, 1)
metric_orig = BinaryLabelDatasetMetric(test_pred_orig, privileged_groups=[{'gender': 1}], unprivileged_groups=[{'gender': 0}])
print("Original Model Bias (Disparate Impact):", metric_orig.disparate_impact())
rew = Reweighing(unprivileged_groups=[{'gender': 0 }], privileged_groups=[{'gender': 1}])
train_rw = rew.fit_transform(train)
model_rw = RandomForestClassifier(random_state=42)
model_rw.fit(train_rw.features, train_rw.labels.ravel())
pred_rw = model_rw.predict(test.features)
test_pred_rw = test.copy()
test_pred_rw.labels = pred_rw.reshape(-1, 1)
metric_rw = BinaryLabelDatasetMetric(test_pred_rw, privileged_groups=[{'gender': 1}], unprivileged_groups=[{'gender': 0}])
print("Model After Reweighing Bias (Disparate Impact):", metric_rw.disparate_impact())

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from aif360.datasets import BinaryLabelDataset
from aif360.algorithms.preprocessing import Reweighing
from aif360.metrics import BinaryLabelDatasetMetric
np.random.seed(42)
n_samples = 200
nationality = np.random.randint(0, 2, n_samples)
threat_score = np.random.rand(n_samples) *10
activity_level = np.random.rand(n_samples) *5
labels = (threat_score + activity_level + nationality*0.5 > 10).astype(int)
df = pd.DataFrame({'nationality': nationality, 'threat_score': threat_score, 'activity_level': activity_level, 'label': labels})
dataset = BinaryLabelDataset(df=df, label_names=['label'], protected_attribute_names=['nationality'])
train, test = dataset.split([0.7], shuffle=True, seed=42)
model_orig = RandomForestClassifier(random_state=42)
model_orig.fit(train.features, train.labels.ravel())
pred_orig = model_orig.predict(test.features)
test_pred_orig = test.copy()
test_pred_orig.labels = pred_orig.reshape(-1, 1)
metric_orig = BinaryLabelDatasetMetric(test_pred_orig, privileged_groups=[{'nationality': 1}], unprivileged_groups=[{'nationality': 0}])
print("Original Model Bias (Disparate Impact):", metric_orig.disparate_impact())
rew = Reweighing(unprivileged_groups=[{'nationality': 0}], privileged_groups=[{'nationality': 1}])
train_rw = rew.fit_transform(train)
model_rw = RandomForestClassifier(random_state=42)
model_rw.fit(train_rw.features, train_rw.labels.ravel())
pred_rw = model_rw.predict(test.features)
test_pred_rw = test.copy()
test_pred_rw.labels = pred_rw.reshape(-1, 1)
metric_rw = BinaryLabelDatasetMetric(test_pred_rw, privileged_groups=[{'nationality': 1}], unprivileged_groups=[{'nationality': 0}])
print("Model After Reweighing Bias (Disparate Impact):", metric_rw.disparate_impact())