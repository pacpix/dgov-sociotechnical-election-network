"""
Justin Stachofsky
Dr. Gebremedhin
CPTS 591
2 October 2020
Create gml file from GitHub html pages
"""

# stdlib
import csv
import os
import glob

# Third Party Libraries
from bs4 import BeautifulSoup as bs
from github import Github
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

# File where access token stored
#import config

# CSV Filenames
social_nodes_file = 'social_nodes.csv'
technical_nodes_file = 'technical_nodes.csv'
connections_file = 'connections.csv'
technical_connections_file = 'technical_connections.csv'
following_connections_file = 'following_connections.csv'
follower_connections_file = 'follower_connections.csv'
social_technical_connections_file = 'social_technical_connections.csv'


# Main program flow
def main():

    # Build csv of individual connections and csv of unique nodes
    create_csv_files()
    # Anonymizes social nodes
    anonymize_dataset()
    # Creates graph and writes it to gml file
    create_gml_file()

# Removes names from social node connections
def anonymize_dataset():

    # Create a dictionary of social node names and anonymized node names
    i = 1
    node_dict = {}
    with open(social_nodes_file, 'r') as socfile:
        csv_reader = csv.reader(socfile)
        next(csv_reader)
        for row in csv_reader:
            node_dict.update({row[0]:'S' + str(i)})
            i = i + 1

    # Open connections and social nodes files and store them in string variables
    connections = open(connections_file, 'r')
    connections = ''.join([j for j in connections]) 
    socnodes = open(social_nodes_file, 'r')
    socnodes = ''.join([j for j in socnodes])
    soctechcons = open(social_technical_connections_file, 'r')
    soctechcons = ''.join([j for j in soctechcons])

    # Find and replace dictionary values in string
    for k, v in node_dict.items():
        connections = connections.replace(k, v)
        socnodes = socnodes.replace(k,v)
        soctechcons = soctechcons.replace(k,v)
    
    # Write strings back into source csv
    csv_writer = open(connections_file, 'w')
    csv_writer.writelines(connections)
    csv_writer.close()
    csv_writer = open(social_nodes_file, 'w')
    csv_writer.writelines(socnodes)
    csv_writer.close()
    csv_writer = open(social_technical_connections_file, 'w')
    csv_writer.writelines(soctechcons)
    csv_writer.close()

    # Delete temporary csv files
    os.remove(following_connections_file)
    os.remove(follower_connections_file)


        

# Appends follower and following connections to main connections csv
def append_following_and_follower_connections():

    with open(connections_file, 'a') as confile:
        with open(following_connections_file, 'r') as followfile:
            csv_reader = csv.reader(followfile)
            csv_writer = csv.writer(confile, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                # Connects contributor to following
                csv_writer.writerow(row)
    
    with open(connections_file, 'a') as confile:
        with open(follower_connections_file, 'r') as followfile:
            csv_reader = csv.reader(followfile)
            csv_writer = csv.writer(confile, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                # Connects follower to contributor
                csv_writer.writerow([row[1], row[0]])


# Adds followers and following to social nodes
def append_following_and_follower_nodes():

    with open(social_nodes_file, 'a') as socfile:
        with open(following_connections_file, 'r') as followfile:
            csv_reader = csv.reader(followfile)
            csv_writer = csv.writer(socfile, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                # Connects repo to repo
                csv_writer.writerow([row[1]])
    
    with open(social_nodes_file, 'a') as socfile:
        with open(follower_connections_file, 'r') as followfile:
            csv_reader = csv.reader(followfile)
            csv_writer = csv.writer(socfile, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                # Connects repo to repo
                csv_writer.writerow([row[1]])


# Adds technical node to technical node connections
def append_technical_connections():

    with open(connections_file, 'a') as confile:
        with open(technical_connections_file, 'r') as techfile:
            csv_reader = csv.reader(techfile)
            csv_writer = csv.writer(confile, delimiter=',')
            for row in csv_reader:
                # Connects repo to repo
                csv_writer.writerow(row)


# Append lines to nodes csv
def append_to_nodes_csv(repo_node, contributor_list):

    with open(technical_nodes_file, 'a') as csv_file:
        # Add repo node
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow([repo_node])

    with open(social_nodes_file, 'a') as csv_file:
        # Add contributor nodes
        csv_writer = csv.writer(csv_file, delimiter=',')
        for contributor in contributor_list:
            csv_writer.writerow([contributor])


# Append lines to connections csv
def append_to_soctech_connections_csv(repo_node, contributor_list):

    with open(social_technical_connections_file, 'a') as csv_file:
        # Connects developer to repo
        csv_writer = csv.writer(csv_file, delimiter=',')
        for contributor in contributor_list:
            csv_writer.writerow([contributor, repo_node])


# Create CSV of connections
def create_csv_files():
    
    # Add title row to contributor nodes csv file
    with open(social_nodes_file, mode='w+') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(['Name'])

    # Add title row to technical nodes csv file
    with open(technical_nodes_file, mode='w+') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(['Name'])

    # Add title row to connections csv file
    with open(connections_file, mode='w+') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(['Source_Node', 'Destination_Node'])

    # Add title row to following connections csv file
    with open(following_connections_file, mode='w+') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(['Contributor', 'Following'])
    
    # Add title row to followers connections csv file
    with open(follower_connections_file, mode='w+') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')
        csv_writer.writerow(['Contributor', 'Follower'])
    
    # Path to htm files with contributor lists
    path = os.getcwd() + '/Repository_Contributors_2020-04-13/*.htm'

    # Glob is list of htm files at path
    for htm in glob.glob(path):
        repo = get_repo_name(htm)
        contributors = get_repo_contributors(htm)
        append_to_nodes_csv(repo, contributors)
        append_to_soctech_connections_csv(repo, contributors)


    # Remove duplicates first, then make api calls
    remove_duplicate_nodes(social_nodes_file)
    get_following_and_follower_api()

    # Add social nodes from following and followers
    append_following_and_follower_nodes()
    
    # Remove duplicate nodes from csv
    remove_duplicate_nodes(social_nodes_file)
    remove_duplicate_nodes(technical_nodes_file)
    
    # Add remaining connections manually
    append_technical_connections()
    append_following_and_follower_connections()


def create_gml_file():

    # Create lists of social nodes, technical nodes, and connections
    with open(social_nodes_file, mode='r') as sn_file:
        next(sn_file)
        social_nodes = [line.rstrip('\n') for line in sn_file]

    with open(technical_nodes_file, mode='r') as tn_file:
        next(tn_file)
        technical_nodes = [line.rstrip('\n') for line in tn_file]

    # In earlier versions "Connections" was all edges
    # Now it is only social --> social
    with open(connections_file, mode='r') as con_file:
        csv_reader = csv.reader(con_file)
        next(csv_reader)
        connections = [tuple(row) for row in csv_reader]
    
    with open(technical_connections_file, mode='r') as tcon_file:
        csv_reader = csv.reader(tcon_file)
        technical_connections = [tuple(row) for row in csv_reader]

    with open (social_technical_connections_file, mode = 'r') as stcon_file:
        csv_reader = csv.reader(stcon_file)
        sociotechnical_connections = [tuple(row) for row in csv_reader]

    # Create graph add nodes and edges
    st_graph = nx.DiGraph()
    st_graph.add_nodes_from(social_nodes, repo=0)
    st_graph.add_nodes_from(technical_nodes, repo=1)
    st_graph.add_edges_from(connections, soc=1, tech=0, soctech=0)
    st_graph.add_edges_from(technical_connections, soc=0, tech=1, soctech=0)
    st_graph.add_edges_from(sociotechnical_connections, soc=0, tech=0, soctech=1)

    # Write network to gml file
    nx.write_gml(st_graph, 'st_graph.gml')


# API calls to populate following and followers connections CSVs
def get_following_and_follower_api():
    
    git = Github(config.token)

    # Following
    with open(following_connections_file, 'a') as csv_file: 
        with open(social_nodes_file, 'r') as socfile:
            # Add following nodes
            csv_writer = csv.writer(csv_file, delimiter=',')
            csv_reader = csv.reader(socfile, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                try:
                    for user in git.get_user(row[0].lstrip('@')).get_following():
                        csv_writer.writerow([row[0], '@' + user.login])
                except Exception as ex:
                    print(ex)
                    print(row[0])

    # Followers
    with open(follower_connections_file, 'a') as csv_file: 
        with open(social_nodes_file, 'r') as socfile:
            # Add following nodes
            csv_writer = csv.writer(csv_file, delimiter=',')
            csv_reader = csv.reader(socfile, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                try:
                    for user in git.get_user(row[0].lstrip('@')).get_followers():
                        csv_writer.writerow([row[0], '@' + user.login])
                except Exception as ex: 
                    print(ex)
                    print(row[0])


# Get list of repo contributors from htm file
def get_repo_contributors(fname):

    # The contributor names are in the 'alt' attribute of each img tag
    with open(fname, 'r') as file:
        contents = file.read()
        soup = bs(contents, features='lxml')
        contributors = [img.get('alt') for img in soup.find_all(
            'img', {'class': 'avatar mr-2', 'alt': True})]

    return contributors


# Get repo name from file name
def get_repo_name(fname):

    # Get file name without path and extension
    repo = os.path.basename(fname)
    repo = os.path.splitext(repo)[0]

    return repo


# Remove duplicate nodes from nodes csv
def remove_duplicate_nodes(dupe_file):

    csv_file = pd.read_csv(dupe_file)
    csv_file.drop_duplicates(inplace=True)
    csv_file.to_csv(dupe_file, index=False)


# Start program exection at main
if __name__ == '__main__':
    main()
