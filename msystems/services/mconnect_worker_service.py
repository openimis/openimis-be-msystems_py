import logging

from msystems.client.mconnect import MConnectClient

logger = logging.getLogger(__name__)


class MConnectWorkerService:
    _client: MConnectClient

    def __init__(self):
        self._client = MConnectClient()

    def fetch_worker_data(self, idnp, user, eu):
        try:
            response = self._client.get_person(idnp, user, eu)

            return {
                "success": True,
                "data": response
            }
        except Exception as e:
            logger.error("Fetch Worker Data Failed", exc_info=e)
            return {
                "success": False,
                "error": "Fetch Worker Data Failed",
                "detail": str(e)
            }
