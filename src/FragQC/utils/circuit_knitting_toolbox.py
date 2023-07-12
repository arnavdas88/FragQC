def path_map_subcircuit(subcircuits, complete_path_map):
    '''
    {
        "circuit": <circuit object at 0x7f4887935510>,
        "pathmap": ...,
        "easy_map": [1, 2, 4]
    }
    '''
    segregated_pathmap = {}
    for base_register, mapping in complete_path_map.items():
        for subcircuit_register in mapping:
            if subcircuit_register['subcircuit_idx'] not in segregated_pathmap:
                segregated_pathmap[subcircuit_register['subcircuit_idx']] = []
            segregated_pathmap[subcircuit_register['subcircuit_idx']].append({"base_register" : base_register, **subcircuit_register})
    result = []
    for subcircuit_index, subcircuit in enumerate(subcircuits):
        subcircuit_details = {
            "circuit": subcircuit,
            "pathmap": segregated_pathmap[subcircuit_index],
            "easy_map": [pathmap['base_register'].index for pathmap in sorted(segregated_pathmap[subcircuit_index], key=lambda x: x['subcircuit_qubit'].index) ]
        }

        result.append(subcircuit_details)
    
    return result

def replace_from_base_map(base_map, new_map):
    for x, row in enumerate(base_map):
        for y, value in enumerate(row):
            new_map[x][y] = base_map[value]
    return new_map