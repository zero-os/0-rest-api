def get_container(service, force=True):
    containers = service.producers.get('container')
    if not containers:
        if force:
            raise RuntimeError('Service didn\'t consume any containers')
        else:
            return
    return containers[0]


def init(job):
    from zeroos.orchestrator.configuration import get_configuration

    service = job.service
    container_actor = service.aysrepo.actorGet('container')
    config = get_configuration(service.aysrepo)

    args = {
        'node': service.model.data.node,
        'flist': config.get(
            'influxdb-flist', 'https://hub.gig.tech/gig-official-apps/influxdb.flist'),
        'hostNetworking': True
    }
    cont_service = container_actor.serviceCreate(instance='{}_influxdb'.format(service.name), args=args)
    service.consume(cont_service)


def install(job):
    start(job)


def start(job):
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.sal.influxdb.influxdb import InfluxDB
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    service.model.data.status = 'running'
    container = get_container(service)
    container.executeAction('start', context=job.context)
    container_ays = Container.from_ays(container, job.context['token'], logger=service.logger)
    influx = InfluxDB(
        container_ays, service.parent.model.data.redisAddr, service.model.data.port,
        service.model.data.rpcport)
    influx.start()

    influx.create_databases(service.model.data.databases)
    service.saveAll()


def stop(job):
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.sal.influxdb.influxdb import InfluxDB
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)

    service = job.service
    service.model.data.status = 'halted'
    container = get_container(service)
    container_ays = Container.from_ays(container, job.context['token'], logger=service.logger)

    if container_ays.is_running():
        influx = InfluxDB(
            container_ays, service.parent.model.data.redisAddr, service.model.data.port,
            service.model.data.rpcport)
        influx.stop()
        container.executeAction('stop', context=job.context)
    service.model.data.status = 'halted'
    service.saveAll()


def uninstall(job):
    from zeroos.orchestrator.configuration import get_jwt_token

    job.context['token'] = get_jwt_token(job.service.aysrepo)
    service = job.service
    container = get_container(service, False)

    if container:
        stop()
        container.delete()
    service.delete()


def processChange(job):
    from zeroos.orchestrator.sal.Container import Container
    from zeroos.orchestrator.sal.influxdb.influxdb import InfluxDB
    from zeroos.orchestrator.configuration import get_jwt_token_from_job

    service = job.service
    args = job.model.args
    if args.pop('changeCategory') != 'dataschema' or service.model.actionsState['install'] in ['new', 'scheduled']:
        return

    container_service = get_container(service)

    container = Container.from_ays(container_service, get_jwt_token_from_job(job), logger=service.logger)
    influx = InfluxDB(
        container, service.parent.model.data.redisAddr, service.model.data.port,
        service.model.data.rpcport)

    if 'port' in args:
        service.model.data.port = args['port']
        if container.is_running() and influx.is_running()[0]:
            influx.stop()
            influx.port = args['port']
            influx.start()

    if args.get('databases'):
        if container.is_running() and influx.is_running()[0]:
            create_dbs = set(args['databases']) - set(service.model.data.databases)
            drop_dbs = set(service.model.data.databases) - set(args['databases'])
            influx.create_databases(create_dbs)
            influx.drop_databases(drop_dbs)
        service.model.data.databases = args['databases']

    service.saveAll()


def monitor(job):
    pass


def init_actions_(service, args):
    return {
        'init': [],
        'install': ['init'],
        'monitor': ['start'],
        'delete': ['uninstall'],
        'uninstall': [],
    }