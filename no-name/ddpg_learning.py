import numpy as np
from itertools import count

from utils import plotting
from agents.ddpg_low_dim import update_
from agents.ddpg_low_dim import DDPG

def ddpg_learning(
        env,
        random_process,
        agent,
        num_episodes,
        gamma=1.0
):
    """The Deep Deterministic Policy Gradient algorithm.
    Parameters
    ----------
    env: gym.Env
        gym environment to train on.
    random_process: Defined in utils.random_process
        The process that add noise for exploration in deterministic policy.
    agent:
        a DDPG agent consists of a actor and critic.
    num_episodes:
        Number of episodes to run for.
    gamma: float
        Discount Factor
    log_every_n_eps: int
        Log and plot training info every n episodes.
    """
    ###############
    # RUN ENV     #
    ###############
    stats = plotting.EpisodeStats(
        episode_lengths=[],
        episode_rewards=[],
        mean_rewards=[])
    total_timestep = 0

    for i_episode in range(num_episodes):
        state = env.reset()
        random_process.reset_states()

        episode_reward = 0
        for t in count(1):
            action = agent.select_action(state)
            # Add noise for exploration
            noise = random_process.sample()[0]
            action += noise
            action = np.clip(action, -1.0, 1.0)
            next_state, reward, done, _ = env.step(action)
            # Update statistics
            total_timestep += 1
            episode_reward += reward
            episode_length = t
            # Store transition in replay memory
            agent.replay_memory.push(state, action, reward, next_state, done)
            # Update
            # agent.update(gamma)
            if total_timestep > 500:
                assert isinstance(agent, DDPG)
                update_(actor_net=agent.actor, critic_net=agent.critic,
                        target_actor_net=agent.target_actor, target_critic_net=agent.target_critic,
                        replay_buffer=agent.replay_memory, batch_size=agent.batch_size,gamma=gamma)
            if done:
                stats.episode_lengths.append(episode_length)
                stats.episode_rewards.append(episode_reward)
                mean_reward = np.mean(stats.episode_rewards[-100:])
                stats.mean_rewards.append(mean_reward)
                print("episode:%d, reward:%.7f" % (i_episode, episode_reward))
                break
            else:
                state = next_state

        if i_episode % 10 == 0:
            pass
            print("### EPISODE %d ### TAKES %d TIMESTEPS" % (i_episode + 1, stats.episode_lengths[i_episode]))
            print("MEAN REWARD (100 episodes): " + "%.3f" % (mean_reward))
            print("TOTAL TIMESTEPS SO FAR: %d" % (total_timestep))
            plotting.plot_episode_stats(stats)

    return stats
