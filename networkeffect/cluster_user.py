import numpy as np
import numpy.random
import csv
import os

import matplotlib.pyplot as plt

### The following code stochastically clusters users by relative order frequencies ###

# load relavent data
def load_data():
	orders = open(os.getcwd() + '/../data/bigfiles/master_orders.txt', "rt", encoding="utf8")
	users = open(os.getcwd() + '/../data/bigfiles/master_users.txt', "rt", encoding="utf8")
	stores = open(os.getcwd() + '/../data/bigfiles/master_stores.txt', "rt", encoding="utf8")
	orders_reader  = csv.DictReader(orders)
	users_reader = csv.DictReader(users)
	stores_reader =csv.DictReader(stores)

	# iterate through stores to compile list of all store _id
	store_ids = []
	for store in stores_reader:
		store_ids.append(store['_id'])

	# iterate through all users to initialize orders by users
	# {user_id : {store_id: num_sent + num_recieved}}
	orders_by_user = {}
	for user in users_reader:
		orders_by_user[user] = {store: 0 for store in store_ids}

	# iterate through orders to compile lists of orders by users
	for order in orders_reader:
		sent_from, sent_to = order['fromUser'], order['toUser']
		store = order['store']

		if sent_from not in orders_by_user:
			orders_by_user[sent_from] = {}
		if sent_to not in orders_by_user:
			orders_by_user[sent_to] = {}

		if store not in orders_by_user[sent_from]:
			orders_by_user[sent_from][store] = 0
		if store not in orders_by_user[sent_to]:
			orders_by_user[sent_to][store] = 0

		orders_by_user[sent_from][store] += 1
		orders_by_user[sent_to][store] += 1

	# normalize num_sent + num_recieved to [0, 1]
	for user in orders_by_user:
		counts_by_store = orders_by_user[user]
		# compute maximum num_sent + num_recieved
		max_count = max([counts_by_store[key] for key in counts_by_store])
		# normalize with respect to max_count and replace in orders_by_user
		orders_by_user[user] = {key: counts_by_store[key] / max_count for key in counts_by_store}

	# convert user representation for numpy processing
	user_ids = [user for user in orders_by_user]
	users = [[orders_by_user[user][store] for store in stores] for user in orders_by_user]
	user_ids, users = np.array(user_ids), np.array(users)

	return user_ids, users


# standard clustering algorithm for user order distribution, K clusters
def cluster(K: int, users):
	# initialize normalized cluster means for each cluster (K total clusters)
	cluster_means = np.random.rand(K, users.shape[1]) * (np.max(users, axis=0) - np.min(users, axis=0)) + np.min(users, axis=0)
	# initialize clusters for each user
	user_clusters, user_count = np.zeros(len(users), int), len(users)
	# set users to cluster closest to them using distance function
	changing = True
	while changing:
		changing = False
		for i in range(user_count):
			min_dist, cluster = np.Inf, None
			for j in range(K):
				trial_dist = distance(users[i], cluster_means[j])
				if trial_dist < min_dist:
					min_dist = trial_dist
					cluster = j

			assert(cluster is not None)

			if user_clusters[i] != cluster:
				changing = True

			user_clusters = cluster

	# reset cluster means based off of new compatriats
	for i, mean in enumerate(np.array([users[user_clusters == i].mean(0) for i in range(K)])):
		if not np.any(np.isnan(mean)):
			cluster_means[i] = mean

	return user_clusters, cluster_means


# computes regular distance between two points
def distance(A, B):
	return np.sum((A-B) ** 2)


# computers scatter loss given cluster output
def scatter(K, users, user_clusters, cluster_means):
	sum_ = 0
	for cluster in range(K):
		group = np.array(users[user_clusters == cluster])
		for el in group:
			sum_ += len(group) * distance(el, cluster_means[cluster])
	return sum_


# plot loss as a function of k
def plot_k():
	_, users = load_data()
	k, scatter_ = [], []
	for i in range(1, 20):
		user_clusters, cluster_means = cluster(i, users)
		k.append(i)
		scatter_.append(scatter(i, users, user_clusters, cluster_means))
	plt.xlabel('K')
	plt.ylabel('Cluster Point Scatter')
	plt.legend()
	plt.title('Cluster Graph for K = 3')
	plt.plot(k_, scatter_)
	plt.show()

# computes user clusters, overwrites results 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-k', type=int)
    parser.add_argument('-plot_k', action='store_true', default=False, help='plot loss as function of k')
    args = parser.parse_args()

    if args.plot_k:
    	plot_k()
    	exit()
