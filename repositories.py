import json
import ConfigParser
import os

config = ConfigParser.ConfigParser()
config.read("config.ini")


class Repositories:

    def __init__(self, client):
        self.client = client
        self.items = []
        self.count = 0
        self.pr_count = 0

    def refresh(self):
        self.count = 0
        self.pr_count = 0
        cursor = ""
        iteration = 0
        while True:
            iteration = iteration + 1

            result = self.client.execute(self.get_query(100, cursor))

            if config.getboolean("General", "refreshFixtures"):
                self.write_result(result, iteration)
            if config.getboolean("General", "debug"):
                print(result)

            parsed_result = json.loads(result)

            if len(parsed_result["data"]["organization"]["repositories"]["edges"]) == 0:
                break

            for item in parsed_result["data"]["organization"]["repositories"]["edges"]:
                self.count = self.count + 1
                self.pr_count = self.pr_count + item["node"]["pullRequests"]["totalCount"]
                cursor = item["cursor"]
                self.items.append(self.build_tuple(item))

            self.sort_repos()

    def sort_repos(self):
        self.items = sorted(self.items, key=lambda repos: repos["pr_count"], reverse=True)

    def get_base_query(self):
        return self.get_file_contents("resources/query-base.graphql")

    def get_query(self, num_items, cursor):
        template = self.get_base_query()

        first = "first: " + str(num_items)
        after = ", after: \"" + cursor + "\"" if cursor != "" else ""

        template = template.replace("first: 100", first + after)

        if config.getboolean("General", "debug"):
            print(template)

        return template

    @staticmethod
    def build_tuple(item):
        return {
            "name": item["node"]["name"],
            "pr_count": item["node"]["pullRequests"]["totalCount"],
            "oldest_pr": {
                "number": item["node"]["pullRequests"]["nodes"][0]["number"]
                if len(item["node"]["pullRequests"]["nodes"]) > 0 else "",
                "title": item["node"]["pullRequests"]["nodes"][0]["title"]
                if len(item["node"]["pullRequests"]["nodes"]) > 0 else "",
                "createdAt": item["node"]["pullRequests"]["nodes"][0]["createdAt"]
                if len(item["node"]["pullRequests"]["nodes"]) > 0 else ""
            }
        }

    @staticmethod
    def write_result(result, iteration):
        path = "test/fixtures"
        if not os.path.exists(path):
            os.makedirs(path)
        result_file = open(path + "/repos-" + str(iteration) + ".json", "w")
        result_file.write(result)
        result_file.close()

    @staticmethod
    def get_file_contents(file_name):
        requested_file = open(file_name, "r")
        return requested_file.read()
