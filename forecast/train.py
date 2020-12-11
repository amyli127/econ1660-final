import argparse
import os
from numpy import genfromtxt
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
import numpy as np
import graphviz
import pandas as pd
import random


def load_data():
	data = genfromtxt(os.getcwd() + '/data/bigfiles/sequence.txt', delimiter=",", skip_header=1)

	data = pd.DataFrame(data)

	final_features = ['orders', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
		 		'Breakfast', 'Lunch', 'Dinner', '# Orders Previous Meal In Snackpass', '# Orders Past 24 Hrs', '# Orders Past 3 Days',
				'# Orders Past 7 Days', '# Orders Past 30 Days', "% Orders Same Meal In Sem.",
				"% Orders Same Day of Week In Sem.", 'Feels Like Temp.', 'Rain Amt.', 'Snow Amt.',
				'Avg. # Orders / Week In Sem', 'Avg. # Orders / Week All-time', 'Avg. # Orders Same Day Of Week & Meal In Sem']

	data.columns = final_features

	X, y = data.iloc[:, 1:], data.iloc[:, 0]

	return X, y

def train(X_train, y_train, args):
	model = xgb.XGBRegressor(**vars(args))
	model.fit(X_train, y_train, eval_set = [(X_train, y_train), (X_test, y_test)], early_stopping_rounds=15, verbose = True)
	return model

def test(model, X_test, y_test):
	y_pred = model.predict(X_test)
	predictions = [1 if value > .25 else 0 for value in y_pred]

	accuracy = accuracy_score(y_test, predictions)
	print("Accuracy: %.2f%%" % (accuracy * 100.0))

	y_test = y_test.tolist()

	pred_yes_count = 0
	pred_yes_actual_yes = 0

	actual_yes = 0
	actual_yes_pred_yes = 0
	for i, pred in enumerate(predictions):
		if pred == 1:
			pred_yes_count += 1
			pred_yes_actual_yes += y_test[i]
		if y_test[i] == 1:
			actual_yes += 1
			actual_yes_pred_yes += pred

	print('predicted yes:', pred_yes_count)
	print('among the times we predicted there would be an order, this is how many times there was an order: ', pred_yes_actual_yes)
	print('% predicted there was an order correctly', pred_yes_actual_yes / pred_yes_count)
	print('actually yes:', actual_yes)
	print('among the times there was an order, this is how many times we predicted there would be an order: ', actual_yes_pred_yes)
	print("% of the orders that were predicted", actual_yes_pred_yes / actual_yes)
	return accuracy, pred_yes_count, pred_yes_actual_yes, actual_yes, actual_yes_pred_yes

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	
	# default
	parser.add_argument('-learning_rate', type=float, default=.1)
	parser.add_argument('-max_depth', type=int, default=5)
	parser.add_argument('-n_estimators', type=int, default=15) # 300
	parser.add_argument('-colsample_bytree', type=float, default=.8)
	parser.add_argument('-subsample', type=float, default=.8)

	args = parser.parse_args()

	print('loading data')
	X, y = load_data()
	print('done')

	# at .25 % threshold
	acc = [] # 93%, 97% 
	acc_when_py = [] # 22%, 
	acc_when_ay = [] # 43%

	for i in range(1):
		seed = random.randint(1, 1000)
		test_size = 0.2
		X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=seed)
		
		print('training model')
		model = train(X_train, y_train, args)
		print('done')
		print('testing test data')
		accuracy, py, pyay, ay, aypy = test(model, X_test, y_test)

		acc.append(accuracy)
		acc_when_py.append(pyay / py)
		acc_when_ay.append(aypy / ay)

		print('testing train data')
		accuracy, py, pyay, ay, aypy = test(model, X_train, y_train)


	my_dict = {'Accuracy': acc, 'Accuracy When Pred. Y': acc_when_py, 'Accuracy When Act. Y': acc_when_ay}
	fig, ax = plt.subplots()
	ax.boxplot(my_dict.values())
	ax.set_xticklabels(my_dict.keys())
	plt.show()

	xgb.plot_importance(model, title='Feature Importance: Weight')
	plt.rcParams['figure.figsize'] = [10, 5]
	plt.show()

	xgb.plot_importance(model, importance_type='gain', title='Feature Importance: Gain')
	plt.rcParams['figure.figsize'] = [10, 5]
	plt.show()

	xgb.plot_importance(model, importance_type='cover', title='Feature Importance: Cover')
	plt.rcParams['figure.figsize'] = [10, 5]
	plt.show()