#EDA on 2var linear regression
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

np.random.seed(0)
X = np.random.rand(100, 1)
y = 2 + 3 * X + np.random.randn(100, 1)
data = pd.DataFrame(data=np.hstack([X, y]), columns=['X', 'y'])
plt.figure(figsize=(8, 6))
plt.scatter(data['X'], data['y'])
plt.title('Scatter plot of X vs y')
plt.xlabel('X')
plt.ylabel('y')
plt.show()
correlation = data['X'].corr(data['y'])
print(f'Correlation coefficient between X and y: {correlation}')
model = LinearRegression()
model.fit(X, y)
intercept = model.intercept_[0]
slope = model.coef_[0][0]
print(f'Intercept: {intercept}')
print(f'Slope: {slope}')
plt.figure(figsize=(8, 6))
plt.scatter(data['X'], data['y'])
plt.plot(data['X'], model.predict(X), color='red')
plt.title('Linear regression model')
plt.xlabel('X')
plt.ylabel('y')
plt.show()