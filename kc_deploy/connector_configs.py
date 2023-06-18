import dictdiffer
def generate_changes(target_connector_configs, active_connector_configs):
    target_connector_configs_by_name = {c['name']:c for c in target_connector_configs}
    active_connector_configs_by_name = {c['name']:c for c in active_connector_configs}
    '''print(target_connector_configs_by_name)'''
    '''print(active_connector_configs_by_name)'''

    delete_config_ids = set(active_connector_configs_by_name.keys()) - set(target_connector_configs_by_name.keys())
    delete_configs = {c: active_connector_configs_by_name[c] for c in delete_config_ids}
    '''print(delete_config_ids)
    print(delete_configs)'''

    create_config_ids = set(target_connector_configs_by_name.keys()) - set(active_connector_configs_by_name.keys())
    create_configs = {c: target_connector_configs_by_name[c] for c in create_config_ids}
    '''print(create_configs)'''

    matching_config_ids = [c for c in target_connector_configs_by_name.keys() if c in active_connector_configs_by_name.keys()]
    update_configs = {}
    update_configs = {}
    for id in matching_config_ids:
        x = active_connector_configs_by_name[id]
        y = target_connector_configs_by_name[id]
        print(target_connector_configs_by_name[id])
        

    
    for id in matching_config_ids:
        pass
        
        
    
    return (1,3)

def has_changed(connector_config_a, connector_config_b) -> bool:
    """detect changes between two connector configs. Should only check for changes to the config (ignore tasks)"""
    diffs = list(dictdiffer.diff(connector_config_a['config'], connector_config_b['config'], ignore=set(['name'])))
    return True if diffs else False

def print_configs(configs):
    pass