from connector_configs import generate_changes, print_configs

def deploy_apps(target_repo, active_repo, delete=False, dry_run=False):
    target_connector_configs = target_repo.all()
    active_connector_configs = active_repo.all()

    to_delete_connector_configs, to_update_connector_configs = generate_changes(target_connector_configs,
                                                                                active_connector_configs)
    return 1

