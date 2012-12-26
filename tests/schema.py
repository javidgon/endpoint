"""
Scheme declarations.
Please note that exist two different implementations,
depending on if we are asking for either one or
several calls.
"""

schema_batch = {"type": "array",
                "items": {"type": "object",
                        "properties": {
                                       "url": {"type": "string"},
                                       "method": {"type": "string"},
                                       "status": {"type": "integer"},
                                       "requested_at": {"type": "string"},
                                       "log": {"type": "string", "required": False},
                                       "match": {"type": "boolean"}
                                       }
                         }
          }

schema_single = {"type": "object",
                        "properties": {
                                       "url": {"type": "string"},
                                       "method": {"type": "string"},
                                       "status": {"type": "integer"},
                                       "requested_at": {"type": "string"},
                                       "log": {"type": "string", "required": False},
                                       "match": {"type": "boolean"}
                                       }
                }
