
import gymnasium as gym
import numpy as np

# ==========================================
# 1. CREATE THE ENVIRONMENT
# ==========================================

env = gym.make("CartPole-v1")

# ==========================================
# 2. DEFINE STATE DISCRETIZATION
# ==========================================

bins = [
    np.linspace(-2.4, 2.4, 6),
    np.linspace(-3, 3, 6),
    np.linspace(-0.2095, 0.2095, 12),
    np.linspace(-3.5, 3.5, 12)
]

def discretize_state(observation):
    return tuple(
        np.digitize(observation[i], bins[i])
        for i in range(len(observation))
    )

# ==========================================
# 3. CREATE THE Q-TABLE
# ==========================================

q_table = np.zeros((7, 7, 13, 13, 2))

# ==========================================
# 4. SET LEARNING PARAMETERS
# ==========================================

learning_rate = 0.1
discount_factor = 0.99
epsilon = 1.0
epsilon_decay = 0.995
min_epsilon = 0.01

num_episodes = 5000

# ==========================================
# 5. TRAIN THE Q-LEARNING AGENT
# ==========================================

for episode in range(num_episodes):

    observation, info = env.reset()
    state = discretize_state(observation)

    total_reward = 0
    terminated = False
    truncated = False

    while not terminated and not truncated:

        # Exploration or exploitation
        if np.random.random() < epsilon:
            action = env.action_space.sample()
        else:
            action = np.argmax(q_table[state])

        # Apply action
        next_observation, reward, terminated, truncated, info = env.step(action)

        next_state = discretize_state(next_observation)

        # Q-learning update
        old_value = q_table[state][action]

        if terminated:
            next_max = 0
        else:
            next_max = np.max(q_table[next_state])

        new_value = old_value + learning_rate * (
            reward + discount_factor * next_max - old_value
        )

        q_table[state][action] = new_value

        state = next_state
        total_reward += reward

    # Reduce exploration
    epsilon = max(min_epsilon, epsilon * epsilon_decay)

    if (episode + 1) % 500 == 0:
        print(
            f"Episode {episode + 1}: "
            f"Reward = {total_reward}, "
            f"Epsilon = {epsilon:.3f}"
        )

env.close()

# ==========================================
# 6. SAVE THE LEARNED Q-TABLE
# ==========================================

np.save("cartpole_q_table.npy", q_table)

print("Q-learning training completed!")
print("Q-table saved successfully!")

# ==========================================
# 7. TEST THE TRAINED AGENT
# ==========================================

test_env = gym.make("CartPole-v1", render_mode="human")

for episode in range(5):

    observation, info = test_env.reset()

    total_reward = 0
    steps = 0

    terminated = False
    truncated = False

    while not terminated and not truncated:

        state = discretize_state(observation)

        # Choose the best learned action
        action = np.argmax(q_table[state])

        observation, reward, terminated, truncated, info = test_env.step(action)

        total_reward += reward
        steps += 1

    print(f"Test Episode {episode + 1}")
    print(f"Total Reward: {total_reward}")
    print(f"Number of Steps: {steps}")
    print("-------------------------")

test_env.close()
