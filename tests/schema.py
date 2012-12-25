schema_batch = {"type": "array",
          "items": {"type": "object",
                        "properties": {
                                       "url": {"type": "string"},
                                       "status": {"type": "integer"},
                                       "date": {"type": "string"},
                                       "log": {"type": "string", "required": False},
                                       "pass": {"type": "boolean"}
                                       }
                         }
          }

schema_single ={"type": "object",
                        "properties": {
                                       "url": {"type": "string"},
                                       "status": {"type": "integer"},
                                       "date": {"type": "string"},
                                       "log": {"type": "string", "required": False},
                                       "pass": {"type": "boolean"}
                                       }
                }
