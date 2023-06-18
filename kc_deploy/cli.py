import argparse
from repository import get_repository
from service import deploy_apps
'''
argparse is the “recommended command-line parsing module in the Python standard library.” 
It's what you use to get command line arguments into your program.

python deploy_apps/cli.py 
--ecs-cluster grada-sales-dev-ecs-cluster  
-s grada-sales-kafka_connect_app_8083 
--connect-port 8085   
--dir apps/local 
--delete 
--dry-run
'''

def main():
    parser = argparse.ArgumentParser(description='Deploy kafka-connect applications',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--connect-host', help='kafka-connect hostname', default='localhost')
    parser.add_argument('--connect-port', help='kafka-connect port', default=8083)
    parser.add_argument('--ecs-cluster', help='ecs cluster that runs the kafka-connect apps')
    parser.add_argument('-s', '--ecs-service', action='append', dest='ecs_services', help='The ecs services that are running kafka-connect')
    parser.add_argument('--dir', help='directory of kafka-connect applications. The app will scan for nested '
                                      'directories', default='apps/dev')
    
    feature_parser = parser.add_mutually_exclusive_group(required=False)
    feature_parser.add_argument('--delete', dest='delete', action='store_true', help='deletes active connectors in '
                                                                                     'environment if they do not '
                                                                                     'exist in target configuration')
    feature_parser.add_argument('--no-delete', dest='delete', action='store_false', help='does *not* delete active '
                                                                                         'connectors in environment '
                                                                                         'if they do not exist in '
                                                                                         'target configuration')
    parser.set_defaults(delete=False)
    parser.add_argument('--dry-run', dest='dry_run', action='store_true', help='Won\'t make changes to active configuration')
    parser.set_defaults(dry_run=False)
    args = parser.parse_args()
    print(parser)

    target_repo = get_repository(path=args.dir)
    '''print(target_repo.all())'''

    host = args.connect_host
    port = args.connect_port

    print('files from cluster...')
    print(f'connecting to kafka-connect at {host}:{port}')
    active_repo = get_repository(host=host, port=port)
    '''print(active_repo.all())'''

    print('deploying...')
    deploy_apps(target_repo, active_repo, delete=args.delete, dry_run=args.dry_run)


if __name__ == "__main__":
    main()


