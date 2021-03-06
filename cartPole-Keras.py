import gym
import keras
import random
import numpy as np
from statistics import median, mean
from collections import Counter
from keras.models import Sequential
from keras.layers import Dense

LR = 1e-3
env = gym.make('CartPole-v0')
env.reset()
goal_steps = 500
score_requirement = 50
initial_games = 1000

#test!
#test 2!

def initial_population():
    training_data = []
    scores = []
    accepted_scores = []

    # iterate through however many games we want:
    for i in range(initial_games):
        score = 0
        # moves specifically from this environment:
        game_memory = []
        # previous observation that we saw
        prev_observation = []
        # for each frame in 200
        for _ in range(goal_steps):
            # choose random action (0 or 1)
            action = random.randrange(0, 2)
            # do it!
            observation, reward, done, info = env.step(action)

            # notice that the observation is returned FROM the action
            # so we'll store the previous observation here, pairing
            # the prev observation to the action we'll take.
            if len(prev_observation) > 0:
                game_memory.append([prev_observation, action])
            prev_observation = observation
            score += reward
            if done: break

        # IF our score is higher than our threshold, we'd like to save
        # every move we made
        if score >= score_requirement:
            accepted_scores.append(score)
            for data in game_memory:
                # convert to one-hot (this is the output layer for our neural network)
                if data[1] == 1:
                    output = [0, 1]
                elif data[1] == 0:
                    output = [1, 0]

                # saving our training data
                training_data.append([data[0], output])

        # reset env to play again
        env.reset()
        # save overall scores
        scores.append(score)

    # just in case you wanted to reference later
    training_data_save = np.array(training_data)
    np.save('saved.npy', training_data_save)

    # some stats here, to further illustrate the neural network magic!
    print('Average accepted score:', mean(accepted_scores))
    print('Median score for accepted scores:', median(accepted_scores))
    print(Counter(accepted_scores))

    return training_data

def neural_network(input_size):

    ann = Sequential()

    # add hidden layer
    # by adding the first hidden layer it automatically gives us how many inputs we have
    # based on the input
    ann.add(Dense(activation="relu", input_dim=input_size, units=12, kernel_initializer="glorot_uniform"))

    # Add second hidden layer, don't need to say the inputs anymore
    ann.add(Dense(activation="relu", units=24, kernel_initializer="glorot_uniform"))

    # Add third hidden layer
    ann.add(Dense(activation="relu", units=48, kernel_initializer="glorot_uniform"))

    # Add fourth hidden layer
    ann.add(Dense(activation="relu", units=24, kernel_initializer="glorot_uniform"))

    # Add fifth hidden layer
    ann.add(Dense(activation="relu", units=12, kernel_initializer="glorot_uniform"))

    # Adding output layer
    # if you had more than one dependent variable, like if you onehotencoded it
    # you would have units as t - 1, where t is number of variables
    # and you would ave the activation function as softmax
    ann.add(Dense(activation="softmax", units=12, kernel_initializer="glorot_uniform"))

    # Compiling the ANN, which means applying stochastic gradient descent to it
    # using logarithmic loss as loss function, if you have a binary output then
    # algorim is called binary_crossentropy; categorical is categorical_crossentropy
    ann.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    return ann


def train_model(training_data, model=False):
    print(len(training_data[0][0]))
    X = np.array([i[0] for i in training_data]).reshape(-1, len(training_data[0][0]), 1)
    y = [i[1] for i in training_data]
    print("x")
    print(X)
    print("y")
    print(y)

    print(len(X[0]))
    print(len(X))

    if not model:
        model = neural_network(len(X[0]))

    model.fit(X, y, epochs = 5)
    return model


training_data = initial_population()
model = train_model(training_data)

scores = []
choices = []
for each_game in range(10):
    score = 0
    game_memory = []
    prev_obs = []
    env.reset()
    for _ in range(goal_steps):
        env.render()

        if len(prev_obs) == 0:
            action = random.randrange(0, 2)
        else:
            action = np.argmax(model.predict(prev_obs.reshape(-1, len(prev_obs), 1))[0])

        choices.append(action)

        new_observation, reward, done, info = env.step(action)
        prev_obs = new_observation
        game_memory.append([new_observation, action])
        score += reward
        if done: break

    scores.append(score)

print('Average Score:', sum(scores) / len(scores))
print('choice 1:{}  choice 0:{}'.format(choices.count(1) / len(choices), choices.count(0) / len(choices)))
print(score_requirement)
