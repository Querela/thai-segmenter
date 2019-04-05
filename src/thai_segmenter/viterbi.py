def viterbi(obs, states, initp, trans, emiss):
    obs_count = len(obs)
    vtb = [{}]
    path = {}

    # initialize base case
    for state in states:
        vtb[0][state] = initp[state] * emiss[obs[0]][state]
        path[state] = [state]

    # run viterbi for t > 0
    test = obs_count
    for t in range(1, test):
        new_path = {}
        vtb.append({})

        for state in states:
            (prob, max_prev_state) = max(
                (
                    (
                        vtb[t - 1][prev_state]
                        * trans[prev_state][state]
                        * emiss[obs[t]][state]
                    ),
                    prev_state,
                )
                for prev_state in states
            )

            vtb[t][state] = prob
            new_path[state] = path[max_prev_state] + [state]

        (max_prob, state) = max((vtb[t][st], st) for st in states)
        if max_prob < 10e-40:
            (prob, max_state) = max(
                (initp[state] * emiss[obs[t]][state], state) for state in states
            )
            (prev_prob, max_prev_state) = max(
                (vtb[t - 1][state], state) for state in states
            )
            vtb[t][max_state] = prob
            new_path[max_state] = path[max_prev_state] + [max_state]
        elif max_prob < 10e-15:
            for state in states:
                vtb[t][state] *= 10e10

        path = new_path

    (prob, state) = max((vtb[test - 1][st], st) for st in states)
    return path[state]


def viterbi_trigram(obs, states, initp, trans, emiss):
    obs_count = len(obs)
    vtb = [{}]
    path = {}

    # initialize
    for state in states:
        vtb[0][state] = dict()
        path[state] = dict()

    for state in states:
        for tmp_state in states:
            vtb[0][tmp_state][state] = initp[state] * emiss[obs[0]][state]
            path[tmp_state][state] = [state]

    # run viterbi
    for t in range(1, obs_count):
        new_path = {}
        vtb.append({})
        for tmp_state in states:
            vtb[t][tmp_state] = dict()
            new_path[tmp_state] = dict()

        for curr_state in states:
            for prev1 in states:
                (prob, prev2) = max(
                    (
                        vtb[t - 1][prev2][prev1]
                        * trans[prev2][prev1][curr_state]
                        * emiss[obs[t]][curr_state],
                        prev2,
                    )
                    for prev2 in states
                )
                vtb[t][prev1][curr_state] = prob
                new_path[prev1][curr_state] = path[prev2][prev1] + [curr_state]

        path = new_path

        max_prob = max((vtb[t][st2][st1]) for st2 in states for st1 in states)
        if max_prob < 10e-15:
            for st2 in states:
                for st1 in states:
                    vtb[t][st2][st1] *= 10e10

    (prob, prev1, state) = max(
        ((vtb[obs_count - 1][st2][st1]), st2, st1) for st2 in states for st1 in states
    )
    return path[prev1][state]
