#!/usr/bin/env python
# coding: utf-8
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import pandas as pd

data_nn = pd.read_csv(r"E:\0316\data\data.csv")
data_t = pd.read_csv(r"E:\0316\data\data_t.csv")

# NETWORK TOPOLOGIES
n_hidden_1 = 256
n_hidden_2 = 128
n_input = 17
n_classes = 4

# INPUTS AND OUTPUTS
x = tf.placeholder("float", [None, n_input])
y = tf.placeholder("float", [None, n_classes])

# NETWORK PARAMETERS
stddev = 0.1
weights = {
    'w1': tf.Variable(tf.random_normal([n_input, n_hidden_1], stddev=stddev), name="w1"),
    'w2': tf.Variable(tf.random_normal([n_hidden_1, n_hidden_2], stddev=stddev), name="w2"),
    'out': tf.Variable(tf.random_normal([n_hidden_2, n_classes], stddev=stddev), name="wout")
}
biases = {
    'b1': tf.Variable(tf.random_normal([n_hidden_1]), name="b1"),
    'b2': tf.Variable(tf.random_normal([n_hidden_2]), name="b2"),
    'out': tf.Variable(tf.random_normal([n_classes]), name="bout")
}
print("NETWORK READY")


def multilayer_perceptron(_X, _weights, _biases):
    layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(_X, _weights['w1']), _biases['b1']))
    layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, _weights['w2']), _biases['b2']))
    return tf.matmul(layer_2, _weights['out']) + _biases['out']


# PREDICTION
pred = multilayer_perceptron(x, weights, biases)

# LOSS AND OPTIMIZER
cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=y, logits=pred))
optm = tf.train.GradientDescentOptimizer(learning_rate=0.001).minimize(cost)
corr = tf.equal(tf.argmax(pred, 1), tf.argmax(y, 1))
accr = tf.reduce_mean(tf.cast(corr, "float"))

# INITIALIZER
init = tf.global_variables_initializer()
print("FUNCTIONS READY")


training_epochs = 20
batch_size = 100
display_step = 4
# LAUNCH THE GRAPH
sess = tf.Session()
sess.run(init)
# OPTIMIZE
for epoch in range(training_epochs):
    c = []
    avg_cost = 0.
    total_batch = int(len(data_nn) / batch_size)
    # ITERATION
    for i in range(total_batch):
        batch_xs = np.array(data_nn.iloc[100 * i:100 + 100 * i, 0:17])
        batch_ys = np.array(data_nn.iloc[100 * i:100 + 100 * i, 17:21])
        feeds = {x: batch_xs, y: batch_ys}
        sess.run(optm, feed_dict=feeds)
        avg_cost += sess.run(cost, feed_dict=feeds)
        c.append(avg_cost)
    avg_cost = avg_cost / total_batch

    # DISPLAY
    if (epoch + 1) % display_step == 0:
        print("Epoch: %03d/%03d cost: %.9f" % (epoch, training_epochs, avg_cost))
        feeds = {x: batch_xs, y: batch_ys}
        train_acc = sess.run(accr, feed_dict=feeds)
        print("TRAIN ACCURACY: %.3f" % (train_acc))
        feeds = {x: np.array(data_t.iloc[:, 0:17]), y: np.array(data_t.iloc[:, 17:21])}
        test_acc = sess.run(accr, feed_dict=feeds)
        print("TEST ACCURACY: %.3f" % (test_acc))
print("OPTIMIZATION FINISHED")

# b保存模型
saver = tf.train.Saver()
saver.save(sess, r"E:\0316\modle\course_modle.ckpt")

# feeds = {x: np.array(data_fina.iloc[0:1, 0:17])}
# test_acc = sess.run(pred, feed_dict=feeds)
