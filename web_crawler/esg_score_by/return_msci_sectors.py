import json
import os

from pygtrans import Translate

curdir = os.getcwd()


def msci_sector_subsector_list():
    """ get all msci data
    :return: a json format of data
    """
    with open(f"{curdir}\web_crawler\esg_score_by\data\sector_subsector_score_list.json", "r") as file:
        data = json.loads(file.read())
        
    return data


def issue_as_list(whole=False) -> json:
    """
    :param whole: boolean type to determine whether to combine the issues or not
    :return: a json format of data
    """
    with open(f"{curdir}\web_crawler\esg_score_by\data\issue_list.json", "r") as file:
        themes = json.loads(file.read())
    if whole:
        return themes

    issues = []
    for theme in themes:
        issues.extend(themes[theme])
    return issues


def issue_as_whole():
    return issue_as_list(whole=True)


def return_score_by_sector(sector_id: str):
    """ get score of the sector by sector id
    :param sector_id: the id of the sector
    :return: json format, detailed scores info
    """
    msci_list = msci_sector_subsector_list()
    issue_list = issue_as_list()
    whole_issue_list = issue_as_whole()
    data = {"environment": [], "social": [], "governance": []}
    for mc in msci_list:
        if mc["id"] == sector_id:
            for i in range(len(mc["score"])):
                if mc["score"][i] != 0:
                    if issue_list[i] in whole_issue_list["environment"]:
                        data["environment"].append({issue_list[i]: mc["score"][i]})
                    elif issue_list[i] in whole_issue_list["social"]:
                        data["social"].append({issue_list[i]: mc["score"][i]})
                    elif issue_list[i] in whole_issue_list["governance"]:
                        data["governance"].append({issue_list[i]: mc["score"][i]})
            break
    return data


def return_score_by_subsector(subsector_id: str):
    """ get score of the subsector by subsector id
        :param subsector_id: the id of the subsector
        :return: json format, detailed scores info
        """
    msci_list = msci_sector_subsector_list()
    issue_list = issue_as_list()
    whole_issue_list = issue_as_whole()
    data = {"environment": [], "social": [], "governance": []}
    for mc in msci_list:
        if subsector_id.startswith(mc["id"]):
            for mcc in mc["subsectors"]:
                if mcc["id"] == subsector_id:
                    for i in range(len(mcc["score"])):
                        if mcc["score"][i] != 0:
                            if issue_list[i] in whole_issue_list["environment"]:
                                data["environment"].append({issue_list[i]: mcc["score"][i]})
                            elif issue_list[i] in whole_issue_list["social"]:
                                data["social"].append({issue_list[i]: mcc["score"][i]})
                            elif issue_list[i] in whole_issue_list["governance"]:
                                data["governance"].append({issue_list[i]: mcc["score"][i]})
                    break
            break
    return data


def return_sector_subsector_list():
    """ get whole sector-subsector list after categorization
    :return: json format
    """
    msci_list = msci_sector_subsector_list()
    data = []
    for mc in msci_list:
        sub = []
        for ss in mc["subsectors"]:
            sub.append({"subsector_id": ss["id"], "name": ss["name"], "scores": return_score_by_subsector(ss["id"])})
        data.append({"sector_id": mc["id"], "name": mc["name"], "scores": return_score_by_sector(mc["id"]), "subsectors": sub})
    return data
