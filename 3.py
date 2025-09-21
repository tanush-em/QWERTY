# Regression w and wo biad
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

np.random.seed(0)
X = np.random.rand(100, 1)
y = 2 + 3 * X + np.random.randn(100, 1)
model_no_bias = LinearRegression(fit_intercept=False)
model_no_bias.fit(X, y)
model_with_bias = LinearRegression(fit_intercept=True)
model_with_bias.fit(X, y)
plt.figure(figsize=(12, 6))
plt.scatter(X, y, label='Data points')
plt.plot(X, model_no_bias.predict(X), color='red', label='Regression without bias')
plt.plot(X, model_with_bias.predict(X), color='blue', label='Regression with bias')
plt.legend()
plt.title('Linear Regression Model with and without Bias')
plt.xlabel('X')
plt.ylabel('y')
plt.show()
print("Model parameters without bias:")
print(f"Slope: {model_no_bias.coef_[0][0]}")
print("\nModel parameters with bias:")
print(f"Intercept: {model_with_bias.intercept_[0]}")
print(f"Slope: {model_with_bias.coef_[0][0]}")