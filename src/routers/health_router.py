from fastapi import APIRouter

# Init APIRouter
router = APIRouter()


@router.get('/live')
def get_liveness_probe():
    """ Livness Probe for Kubernetes - If this endpoint does not return 200 OK
    The Pod will be restarted

    :return: dict - Status with 200 OK
    """
    return {'status': '200 OK'}


@router.get('/ready')
def get_readiness_probe():
    """ Readiness Probe for Kubernetes to check if Microservices is ready

    :return: dict - Status with 200 OK
    """
    return {'status': '200 OK'}
