from matplotlib import pyplot as plt
import pandas
import re


def parse_agent(agent):
    print(agent)
    possible_agent = re.findall(r"(\w+)/.+", agent)
    if len(possible_agent) > 0:
        return possible_agent[0]
    else:
        return agent.split(" ")[0]


logs = pandas.read_csv("logs.csv")
logs = logs.fillna("not_specified")
logs["parsed_agents"] = logs["agent"].apply(parse_agent)

figure, subplots = plt.subplots(2, 2)

plt.style.use("bmh")
logs["parsed_agents"].value_counts().plot(kind="pie", ylabel="", title="User Agents", ax=subplots[0, 0])
logs.dropna()["method"].value_counts().plot(kind="pie", ylabel="", title="Methods", ax=subplots[0, 1])
logs.dropna()["file"].value_counts().plot(kind="pie", ylabel="", title="Requested File", ax=subplots[1, 0])
logs.dropna()["version"].value_counts().plot(kind="pie", ylabel="", title="HTTP Version", ax=subplots[1, 1])

plt.show()
