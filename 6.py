# Ethics in AI Optimization
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from aif360.datasets import AdultDataset
from aif360.metrics import BinaryLabelDatasetMetric
from aif360.algorithms.preprocessing import Reweighing

dataset_orig = AdultDataset()
privileged_groups = [{'sex': 1}]
unprivileged_groups = [{'sex': 0}]
train, test = dataset_orig.split([0.7], shuffle=True, seed=42)
model_orig = RandomForestClassifier(random_state=42)
model_orig.fit(train.features, train.labels.ravel())
predictions_orig = model_orig.predict(test.features)
test_pred_orig = test.copy()
test_pred_orig.labels = predictions_orig.reshape(-1, 1)
metric_orig = BinaryLabelDatasetMetric(test_pred_orig, privileged_groups=privileged_groups, unprivileged_groups=unprivileged_groups)
print("Original Model Bias (Disparate Impact):")
print(metric_orig.disparate_impact())
rew=Reweighing(unprivileged_groups=unprivileged_groups, privileged_groups=privileged_groups)
train_reweighted = rew.fit_transform(train)
model_reweighted = RandomForestClassifier(random_state=42)
model_reweighted.fit(train_reweighted.features, train_reweighted.labels.ravel())
predictions_reweighted = model_reweighted.predict(test.features)
test_pred_reweighted = test.copy()
test_pred_reweighted.labels = predictions_reweighted.reshape(-1, 1)
metric_reweighted = BinaryLabelDatasetMetric(test_pred_reweighted, privileged_groups=privileged_groups, unprivileged_groups=unprivileged_groups)
print("\nModel After Reweighting Bias (Disparate Impact):")
print(metric_reweighted.disparate_impact())