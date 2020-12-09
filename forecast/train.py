import argparse
from numpy import loadtxt
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


def load_data():
	data = loadtxt(os.getcwd() + '/data/bigfiles/sequence.txt', delimiter=",")
	X, y = data[:, 1:], data[:, 0]

	seed = 7
	test_size = 0.33
	X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=seed)

	return X_train, X_test, y_train, y_test

def train(X_train, y_train, args):
	model = XGBRegressor(**args)
	model.fit(X_train, y_train)
	return model

def test(model, X_test, y_test):
	y_pred = model.predict(X_test)
	predictions = [round(value) for value in y_pred]

	accuracy = accuracy_score(y_test, predictions)
	print("Accuracy: %.2f%%" % (accuracy * 100.0))


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	# required
	parser.add_argument('-learning_rate', type=float, required=True)
	parser.add_argument('-subsample', type=float, required=True)
	# default
	parser.add_argument('-max_depth', type=int, default=5)
	parser.add_argument('-n_estimators', type=int, default=10)

	args = parser.parse_args()


	X_train, X_test, y_train, y_test = train_test_split(X, Y, test_size=test_size, random_state=seed)

	model = train(X_train, y_train, args)

	test(model, X_test, y_test)