#!/usr/bin/env python3.6
"""Start WISE Stack"""

from core import WSCAgentAPI

api = WSCAgentAPI.WSCAgentRestfulAPI()
api.run()