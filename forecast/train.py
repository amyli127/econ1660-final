import argparse
import os
from numpy import genfromtxt
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


def load_data():
	data = genfromtxt(os.getcwd() + '/data/bigfiles/sequence.txt', delimiter=",", skip_header=1)
	X, y = data[:, 1:], data[:, 0]

	seed = 7
	test_size = 0.33
	X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=seed)

	return X_train, X_test, y_train, y_test

def train(X_train, y_train, args):
	model = XGBRegressor(**vars(args))
	model.fit(X_train, y_train)
	return model

def test(model, X_test, y_test):
	y_pred = model.predict(X_test)
	# predictions = [round(value) for value in y_pred]
	predictions = [1 if value > .3 else 0 for value in y_pred]

	accuracy = accuracy_score(y_test, predictions)
	print("Accuracy: %.2f%%" % (accuracy * 100.0))


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
	print('actually yes:', actual_yes)
	print('among the times there was an order, this is how many times we predicted there would be an order: ', actual_yes_pred_yes)
			



if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	# required
	parser.add_argument('-learning_rate', type=float, required=True)
	parser.add_argument('-subsample', type=float, required=True)
	# default
	parser.add_argument('-max_depth', type=int, default=5)
	parser.add_argument('-n_estimators', type=int, default=10)

	args = parser.parse_args()

	print('loading data')
	X_train, X_test, y_train, y_test = load_data()
	print('done')
	print('training model')
	model = train(X_train, y_train, args)
	print('done')
	test(model, X_test, y_test)