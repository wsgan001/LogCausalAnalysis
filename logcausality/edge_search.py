#!/usr/bin/env python
# coding: utf-8

import sys
import os
from collections import defaultdict

import common
import config
import pcresult


def diff_event_type(conf):
    cnt = 0
    for r in pcresult.results(conf):
        dataset_flag = False
        set_undirected = set()
        for edge in r.graph.edges():
            types = [r.evmap.info(eid).type for eid in edge]
            if types[0] == types[1]:
                pass
            else:
                if not dataset_flag:
                    print("# {0}".format(r.filename.partition("/")[-1]))
                    dataset_flag = True
                if (edge[1], edge[0]) in r.graph.edges():
                    directed = False
                    if (edge[1], edge[0]) in set_undirected:
                        pass
                    else:
                        set_undirected.add(edge)
                        r._print_edge(edge, directed)
                        cnt += 1
                else:
                    directed = True
                    r._print_edge(edge, directed)
                    cnt += 1
    print
    print("Edges among different event type: {0}".format(cnt))


def related_filtered(conf):
    cnt = 0
    for r in pcresult.results(conf):
        dataset_flag = False
        for edge in r.graph.edges():
            types = [r.evmap.info(eid).type for eid in edge]
            if types[0] == 0 and types[1] == 0:
                pass
            else:
                if not dataset_flag:
                    print("# {0}".format(r.filename.partition("/")[-1]))
                    dataset_flag = True
                if (edge[1], edge[0]) in r.graph.edges():
                    directed = False
                else:
                    directed = True
                r._print_edge(edge, directed)
                cnt += 1
    print
    print("Edges related to filtered event: {0}".format(cnt))


def related_filtered_all(conf, key = "date"):
    import networkx as nx
    d_nodes = defaultdict(int)
    d_edges = defaultdict(int)
    d_filtered = defaultdict(int)
    for r in pcresult.results(conf):
        key = r.filename.split("_")[-1]
        d_nodes[key] += r.graph.number_of_nodes()
        d_edges[key] += pcresult.number_of_edges(r.graph)
        g = nx.Graph(r.graph)
        for edge in g.edges():
            types = [r.evmap.info(eid).type for eid in edge]
            if types[0] == 0 and types[1] == 0:
                pass
            else:
                d_filtered[key] += 1

    for k in sorted(d_nodes.keys()):
        print("{0} {1} {2} {3}".format(k, d_nodes[k],
                                       d_edges[k], d_filtered[k]))



def list_all_gid(conf):
    import log_db
    import lt_label
    ld = log_db.LogData(conf)
    ll = lt_label.init_ltlabel(conf)

    s_gid = set()
    for r in pcresult.results(conf):
        for edge in r.graph.edges():
            for gid in [r.evmap.info(eid).gid for eid in edge]:
                s_gid.add(gid)

    for gid in s_gid:
        l_ltline = ld.ltg_members(gid)
        print("gid {0} : {1} in {2}".format(gid,
            ll.get_ltg_label(gid, l_ltline)), ll.get_ltg_group(gid, l_ltline))


def search_gid(conf, gid):
    for r in pcresult.results(conf):
        for edge in r.graph.edges():
            for temp_gid in [r.evmap.info(eid).gid for eid in edge]:
                if temp_gid == gid:
                    print r.filename


def diff_evset_edge(conf1, conf2):
    import eventmgr
    d_diff = eventmgr.diff_event_edge(conf1, conf2)

    for r in pcresult.results(conf1):
        dataset_flag = False
        fn = r.filename.split("/")[-1]
        s_evdef = d_diff[fn]
        for edge in r.graph.edges():
            if r.evmap.info(edge[0]) in s_evdef or \
                    r.evmap.info(edge[1]) in s_evdef:
                if not dataset_flag:
                    print("# {0}".format(r.filename.partition("/")[-1]))
                    dataset_flag = True
                directed = (edge[1], edge[0]) in r.graph.edges()
                r._print_edge(edge, directed)
        print


def diff_edge_all(conf1, conf2, flag = None, ac_host = False):

    def get_edge_dict(conf, flag, ac_host):
        d = {}
        for r in pcresult.results(conf):
            fn = r.filename.split("/")[-1]
            d[fn] = set()
            dedges, udedges = r._separate_edges()
            if flag is None:
                edges = dedges + udedges
            elif flag == "directed":
                edges = dedges
            elif flag == "undirected":
                edges = udedges
            else:
                raise ValueError
            for edge in edges:
                cedge = tuple([r.evmap.info(eid) for eid in edge])
                if ac_host and cedge[0].host == cedge[1].host:
                    pass
                else:
                    d[fn].add(cedge)
        return d

    d_c1 = get_edge_dict(conf1, flag, ac_host)
    d_c2 = get_edge_dict(conf2, flag, ac_host)

    cnt_and = 0
    cnt_or = 0
    for key in d_c1.keys():
        assert d_c2.has_key(key)
        cnt_and += len(d_c1[key] & d_c2[key])
        cnt_or += len(d_c1[key] | d_c2[key])
    
    cnt_c1 = sum([len(s) for s in d_c1.values()])
    cnt_c2 = sum([len(s) for s in d_c2.values()])
    if flag is None:
        state_flag = "All edges"
    elif flag == "directed":
        state_flag = "Directed edges"
    elif flag == "undirected":
        state_flag = "Undirected edges"
    if ac_host:
        state_ac = "across hosts"
    else:
        state_ac = ""
    print("# {0} {1}".format(state_flag, state_ac))
    print("{0}: {1}".format(conf1.filename, cnt_c1))
    print("{0}: {1}".format(conf2.filename, cnt_c2))
    print("Union: {0}".format(cnt_and))
    print("Intersection: {0}".format(cnt_or))
    print("Jaccard: {0}".format(1.0 * cnt_and / cnt_or))
    print("Dice: {0}".format(2.0 * cnt_and / (cnt_c1 + cnt_c2)))
    print("Simpson: {0}".format(1.0 * cnt_and / min(cnt_c1, cnt_c2)))
    print


if __name__ == "__main__":
    usage = """
usage: {0} [options] args...
    """.format(sys.argv[0]).strip()

    import optparse
    op = optparse.OptionParser(usage)
    op.add_option("-c", "--config", action="store",
            dest="conf", type="string", default=config.DEFAULT_CONFIG_NAME,
            help="configuration file path")
    (options, args) = op.parse_args()

    conf = config.open_config(options.conf)
    if len(args) == 0:
        sys.exit(usage)

    mode = args.pop(0)
    if mode == "diff-event-type":
        diff_event_type(conf)
    elif mode == "related-filtered":
        related_filtered_all(conf)
    elif mode == "list-all-gid":
        list_all_gid(conf)
    elif mode == "search-gid":
        if len(args) == 0:
            sys.exit("give me gid")
        gid = args[0]
        search_gid(conf, gid)
    elif mode == "diff-evset-edge":
        if len(args) == 0:
            sys.exit("give me another config")
        conf2 = config.open_config(args[0])
        diff_evset_edge(conf, conf2)
    elif mode == "diff-edge":
        if len(args) == 0:
            sys.exit("give me another config")
        conf2 = config.open_config(args[0])
        diff_edge_all(conf, conf2, "directed", False)
        diff_edge_all(conf, conf2, "directed", True)
        diff_edge_all(conf, conf2, "undirected", False)
        diff_edge_all(conf, conf2, "undirected", True)
        diff_edge_all(conf, conf2, None, False)
    else:
        raise NotImplementedError


