import pickle
from itertools import permutations, product
from math import log
from pathlib import Path


class Hidden_State:

    def __init__(self, state):
        self.state = state
        self.pt_num = self.state.index(Player("PT"))

    def __getitem__(self, item):
        return self.state[item]

    def __repr__(self):
        return repr(self.state)

    def __len__(self):
        return len(self.state)

class Hidden_State_Iterator:

    def __init__(self, players):
        self.players = players

    def __iter__(self):
        for hidden_state in permutations(self.players):
            yield Hidden_State(hidden_state)

class Player:

    def __init__(self, role):
        self.role = role

    def __str__(self):
        return roles[self.role]

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.role == other.role

    def __hash__(self):
        return hash(self.role)

good_guys = [Player("PT"), Player("TC")]
bad_guys = [Player("QT"), Player("TS"), Player("TG")]
agents_of_chaos = [Player("TM"), Player("PS")]
everybody = good_guys + bad_guys + agents_of_chaos

roles = {
    "QT" : "Queen Tofu",
    "PT" : "Princess Tofu",
    "TC" : "Tofu Chef",
    "TS" : "Tofu Simp",
    "TG" : "Tofu Guard",
    "PS" : "Pudding spy",
    "TM" : "Tofu Maid"
}

class Question:

    def __init__(self, player_num, _type, they = None):
        self.player_num = player_num
        self.type = _type
        self.they = they

    def possible_answers(self, hidden_state):

        if hidden_state[self.player_num] in bad_guys:

            if self.type == 1:
                ret = list(range(len(hidden_state)))
                del ret[hidden_state.pt_num]
                return ret
            elif self.type == 2:
                ret = list(hidden_state.state)
                del ret[self.they]
                return ret

        elif hidden_state[self.player_num] in good_guys:

            if self.type == 1:
                return [hidden_state.pt_num]
            elif self.type == 2:
                return [hidden_state[self.they]]

        elif hidden_state[self.player_num] in agents_of_chaos:

            if self.type == 1:
                return list(range(len(hidden_state)))
            elif self.type == 2:
                return list(hidden_state)

    def __repr__(self):
        if self.type == 1:
            return f"Question({self.player_num},{self.type})"
        elif self.type == 2:
            return f"Question({self.player_num},{self.type},{self.they})"

    def __eq__(self, other):
        return self.player_num == other.player_num and self.type == other.type and self.they == other.they

    def __hash__(self):
        return hash(self.player_num) + hash(self.type) + hash(self.they)

class Public_State_Iterator:

    def __init__(self, hidden_state):
        self.hidden_state = hidden_state

    def __iter__(self):
        """
        yield: A tuple that makes sense for the hidden state
        Iterate over all permutations of players (not for now)
        iterate over players
        Iterate over questions 1, 2.0, 2.1, ..., 2.n
        Iterate over responses
        """

        all_questions = [(1,)]
        for they in range(len(self.hidden_state)):
            all_questions.append((2,they))

        question_space = product(all_questions, repeat = len(self.hidden_state) - 1)

        for seq in question_space:
            possibility_space = []
            questions = []
            # for _player_num in range(len(self.hidden_state)-1):
            #     q = Question(_player_num+1, *seq[_player_num])
            #     questions.append(q)
            #     possibilities = q.possible_answers(self.hidden_state)
            #     possibility_space.append(possibilities)
            q = Question(1, *seq[0])
            questions.append(q)
            possibilities = q.possible_answers(self.hidden_state)
            possibility_space.append(possibilities)
            for perm in permutations(range(1,len(self.hidden_state)-1)):
                for _player_num in perm:
                    q = Question(_player_num+1, *seq[_player_num])
                    questions.append(q)
                    possibilities = q.possible_answers(self.hidden_state)
                    possibility_space.append(possibilities)


            for responses in product(*tuple(possibility_space)):
                pre_yield = list(zip(questions, responses))
                for q, player_num in product(all_questions, range(1, len(self.hidden_state))):
                    q = Question(player_num, *q)
                    for response in q.possible_answers(self.hidden_state):
                        yield tuple(pre_yield + [(q, response)])

def get_marginal_question_dict(d, q):
    return {
        key : val
        for key,val in d.items()
        if key[0][0] == q
    }

def get_marginal_response_dict(d, q, r):
    return {
        key : val
        for key,val in d.items()
        if key[0] == (q, r)
    }

def get_distribution(d):
    denom = sum(len(val) for val in d.values())
    return {
        key : len(val)/denom
        for key,val in d.items()
    }

def get_entropy(distro):
    return -sum(p*log(p) for p in distro.values())

players = [
    Player("QT"),
    Player("PT"),
    Player("TM"),
    Player("TG")
]

public_states_by_hidden_state = {
    hidden_state : list(Public_State_Iterator(hidden_state))
    for hidden_state in Hidden_State_Iterator(players)
}

public_states = set()
for states in public_states_by_hidden_state.values():
    public_states.update(states)

hidden_states_by_public_state = {
    public_state : [
        hidden_state
        for hidden_state in public_states_by_hidden_state.keys()
        if public_state in public_states_by_hidden_state[hidden_state]
    ]
    for public_state in public_states
}
x=1
# all_questions = []
# for player_num in range(1, len(players)):
#     all_questions.append(Question(player_num, 1))
#     all_questions.extend(
#         Question(player_num, 2, they) for they in range(len(players))
#     )

# marg = hidden_states_by_public_state
#
# for i in range(len(players) + 1):
#     for q in all_questions

# for q in all_questions:
#     marg = get_marginal_question_dict(hidden_states_by_public_state, q)
#     distro = get_distribution(marg)
#     print(get_entropy(distro), q)

