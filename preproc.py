import json
from glob import glob
import os

METHOD = {
    0: 'pinning',
    1: 'aging',
    2: 'incremental',
    3: 'ours',
}

# pair-wise
def pairwise(root, data_name):
    flist = glob(f'{root}/{data_name}/*.json')
    for f in flist:
        base = os.path.splitext(os.path.basename(f))[0]
        method_name = METHOD[int(base.split('_')[1])]
        data = {}
        with open(f, 'r', encoding='utf-8') as fin:
            org_data = json.loads(fin.read())
            data['highlight-slices'] = [slice_id - 1 for slice_id in org_data['highlight-slices']]
            data['highlight-nodes']  = org_data['highlight-points'][0]
            data['timeslices'] = []
            timeslices = org_data['timeslices']
            for timeslice in timeslices:
                node_id   = timeslice['nodes']
                links_org = timeslice['links']
                node_pos  = timeslice['positions']
                # regenerate nodes
                nodes = []
                links = []
                for id in node_id:
                    [x, y] = node_pos[str(id)]
                    nodes.append({
                        'id': id,
                        'x': x,
                        'y': y,
                        'group': 0
                    })
                # regenerate links
                for [source, target] in links_org:
                    links.append({
                        'source': source,
                        'target': target,
                    })
                # regenerate timeslice
                data['timeslices'].append({
                    'nodes': nodes,
                    'links': links,
                })
        
        os.makedirs(f'data/node/{method_name}', exist_ok=True)
        with open(f'data/node/{method_name}/{data_name}.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(data))
            f.flush()

            print(f'[{method_name}] {data_name} done.')


# cluster
def cluster(root, data_name):
    flist = glob(f'{root}/{data_name}_*.json')
    for f in flist:
        base = os.path.splitext(os.path.basename(f))[0]
        method_name = METHOD[int(base.split('_')[1])]
        data = {}
        with open(f, 'r', encoding='utf-8') as fin:
            org_data = json.loads(fin.read())
            data['highlight-slices'] = [slice_id - 1 for slice_id in org_data['highlight-slices']]
            data['highlight-groups']  = org_data['highlight-groups']
            data['timeslices'] = []
            timeslices = org_data['timeslices']
            for timeslice in timeslices:
                node_id   = timeslice['nodes']
                links_org = timeslice['links']
                node_pos  = timeslice['position']
                groups    = timeslice['group']
                # regenerate nodes
                nodes = []
                links = []
                for id in node_id:
                    [x, y] = node_pos[str(id)]
                    nodes.append({
                        'id': id,
                        'x': x,
                        'y': y,
                        'group': groups[str(id)],
                    })
                # regenerate links
                for [source, target] in links_org:
                    links.append({
                        'source': source,
                        'target': target,
                    })
                # regenerate timeslice
                data['timeslices'].append({
                    'nodes': nodes,
                    'links': links,
                })
        
        os.makedirs(f'data/cluster/{method_name}', exist_ok=True)
        with open(f'data/cluster/{method_name}/{data_name}.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(data))
            f.flush()

            print(f'[{method_name}] {data_name} done.')


if __name__ == '__main__':

    os.makedirs('data/node', exist_ok=True)

    pairwise('data/pair-wise', 'ambassador')
    pairwise('data/pair-wise', 'newcomb')
    pairwise('data/pair-wise', 'syn0')
    pairwise('data/pair-wise', 'syn1')
    
    os.makedirs('data/cluster', exist_ok=True)

    cluster('data/cluster_pairwise', 'clu0')
    # cluster('data/cluster_pairwise', 'clu1')
    cluster('data/cluster_pairwise', 'clu2')
    cluster('data/cluster_pairwise', 'clu3')
    cluster('data/cluster_pairwise', 'clu4')
