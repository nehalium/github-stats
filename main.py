from graphqlclient import GraphQLClient
from repositories import Repositories
import ConfigParser

config = ConfigParser.ConfigParser()
config.read("config.ini")


def get_client():
    client = GraphQLClient(config.get("GithubAPI", "url"))
    client.inject_token("bearer " + config.get("GithubAPI", "token"))
    return client


def main():
    client = get_client()

    repos = Repositories(client)
    repos.refresh()

    # Print results
    for item in repos.items:
        print(item["name"] + "\t" + str(item["pr_count"]) + "\t" + item["oldest_pr"]["title"])
    print("=======================================")
    print("Number of repositories: " + str(repos.count))
    print("Number of open pull requests: " + str(repos.pr_count))


if __name__ == '__main__':
    main()
