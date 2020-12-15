import numpy as np

dimensionality = 10


def mse(x, y):
    out = np.sum(np.square(x - y)).flatten()
    return out

mse = np.vectorize(mse)

class KMeans:

    def __init__(self, k):
        self.k = k
        self.lr = 0.01

    def fit(self, X):

        self.centroids = np.random.random((self.k, dimensionality))  # Should not be same

        self.loss = mse

        # Two step algorithm

        has_not_converged = True

        # Multiple restarts, and maximum number of iterations
        threshold = 0.1

        # Until converge
        c = 0
        while has_not_converged:
            c += 1
            print("Iteration: ", c)

            # calculate the similarity matrix
            sim = np.zeros((self.centroids.shape[0], X.shape[0]))

            for i in range(self.centroids.shape[0]):
                for j in range(X.shape[0]):
                    sim[i, j] = mse(self.centroids[i], X[j])[0]

            # Find the centroids assigned to each datapoints
            closest_centroid_to_datapoint_idx = np.argmin(sim, axis=0)

            global_mean_distance = 0.

            for k in range(self.k):
                # print("Looking at centroid idx", k)

                # Pick all data samples that belong to cluster k_
                respective_datasamples = X[closest_centroid_to_datapoint_idx == k]
                # print("Respective datasamples: ", respective_datasamples.shape)

                # print("Respective datasample")

                distance = np.sum(self.loss(respective_datasamples, self.centroids[k].reshape(1, -1)))

                # Calculate the centroid to be the mean of all these datapoints
                new_centroid = np.mean(respective_datasamples, axis=0)
                # print("New centroid shape: ", new_centroid.shape)
                self.centroids[k] = new_centroid

                global_mean_distance += distance

            print("Global mean distance is: ", global_mean_distance / float(X.shape[0]))

            print("Self centroids are:", closest_centroid_to_datapoint_idx)
            if global_mean_distance < threshold:  # or np.equal(old_assignments, closest_centroid_to_datapoint_idx).all()
                print("Converged?", not has_not_converged)
                has_not_converged = False
            else:
                old_assignments = closest_centroid_to_datapoint_idx

        return self.centroids


if __name__ == "__main__":
    print("Start")

    model = KMeans(k=3)

    X = np.random.random((7, 10))

    centroids = model.fit(X)
    print("Centroids are: ")

    print(centroids)
