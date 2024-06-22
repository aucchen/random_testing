from collections import Counter

import networkx as nx

def graph_from_scene_lists(filenames, root_nodes_only=False, threshold=100):
    """
    Given a list of filenames corresponding to scene traversal orders, this constructs a graph...

    For a set of traversals of scenes: there is an edge between scene A and scene B if scene B occurs after scene A in all traversals, and there is no scene C such that C occurs between A and B in all traversals.
    """
    # list of lists of scene names
    # load the scene lists
    scene_lists = []
    for filename in filenames:
        scenes = []
        with open(filename) as f:
            for l in f.readlines():
                l = l.strip()
                if len(l) > 0:
                    scenes.append(l)
        scene_lists.append(scenes)
    # build the ordering
    # TODO: do we do root nodes only?
    # create a dict: for each scene, if x occurs after
    # efficiency concerns: there is a quadratic method to do this. is there an easier way?
    all_scene_adjacencies = []
    all_scene_ids = set()
    for i, scene_list in enumerate(scene_lists):
        scene_adjacency = {}
        for scene in scene_list:
            if scene not in scene_adjacency:
                all_scene_ids.add(scene)
                for k, v in scene_adjacency.items():
                    if k != scene:
                        v.add(scene)
                scene_adjacency[scene] = set()
        all_scene_adjacencies.append(scene_adjacency)
    # potential_adjacencies contains all connections in all traces, along with the count...
    potential_adjacencies = {}
    for scene in all_scene_ids:
        potential_neighbors = Counter()
        for scene_adjacency in all_scene_adjacencies:
            if scene not in scene_adjacency:
                continue
            for s2 in scene_adjacency[scene]:
                potential_neighbors[s2] += 1
        potential_adjacencies[scene] = potential_neighbors
    # temp_ordering is a partial ordering such that if s2 is in temp_ordering[s1], then s2 always occurs after s1.
    temp_ordering = {}
    for s1, potential_neighbors in potential_adjacencies.items():
        final_neighbors = Counter()
        for s2, count in potential_neighbors.items():
            if s1 in potential_adjacencies[s2]:
                continue
            final_neighbors[s2] = count
        # here, final_neighbors contains all nodes such that s2 always appears after s1.
        # now we need further filtering.
        temp_ordering[s1] = final_neighbors
    final_adjacencies = {}
    for s1, neighbors in temp_ordering.items():
        final_neighbors = set()
        for s2, s2_count in neighbors.items():
            if s2_count < threshold:
                continue
            has_intermediate = False
            for s3, n2 in temp_ordering.items():
                if s3 == s1 or s3 == s2:
                    continue
                if s3 in neighbors and s2 in n2 and n2[s2] >= threshold:
                    has_intermediate = True
                    break
            if not has_intermediate:
                final_neighbors.add(s2)
        final_adjacencies[s1] = final_neighbors
        # filter potential neighbors...
    return final_adjacencies

if __name__ == '__main__':
    """
    file_base = 'bee/random_test_outputs_2/'
    filenames = [file_base + f'scenes_{i}.txt' for i in range(10000)]
    adjacencies = graph_from_scene_lists(filenames)

    graph = nx.from_dict_of_lists(adjacencies, create_using=nx.DiGraph)
    nx.write_adjlist(graph, 'bee_graph.txt')
    nx.nx_agraph.write_dot(graph, 'bee.dot')
    """
    """
    file_base = 'beauty_pageant/Social Anxiety Simulator 2019/random_test_outputs_2/'
    filenames = [file_base + f'scenes_{i}.txt' for i in range(1000)]
    adjacencies = graph_from_scene_lists(filenames, threshold=1)

    graph = nx.from_dict_of_lists(adjacencies, create_using=nx.DiGraph)
    nx.write_adjlist(graph, 'nye2019_graph.txt')
    nx.nx_agraph.write_dot(graph, 'nye2019.dot')
    """
    file_base = 'social_democracy/random_test_outputs_2/'
    filenames = [file_base + f'scenes_{i}.txt' for i in range(1000)]
    adjacencies = graph_from_scene_lists(filenames, threshold=1)

    graph = nx.from_dict_of_lists(adjacencies, create_using=nx.DiGraph)
    nx.write_adjlist(graph, 'sd_graph.txt')
    nx.nx_agraph.write_dot(graph, 'sd.dot')
    #graph = nx.read_adjlist('bee_graph.txt')
    # dot -Tsvg bee.dot
