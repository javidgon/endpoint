schema_batch = {"type": "array",
          "items": {"type": "object",
                        "properties": {
                                       "url": {"type": "string", "required": False},
                                       "method": {"type": "string", "required": False},
                                       "status_code": {"type": "integer"},
                                       "requested_at": {"type": "string"},
                                       "log": {"type": "string", "required": False},
                                       "tests_passed": {"type": "boolean"}
                                       }
                         }
          }

schema_single ={"type": "object",
                        "properties": {
                                       "url": {"type": "string"},
                                       "method": {"type": "string"},
                                       "status_code": {"type": "integer"},
                                       "requested_at": {"type": "string"},
                                       "log": {"type": "string", "required": False},
                                       "tests_passed": {"type": "boolean"}
                                       }
                }

schema_error = {"type": "object",
                        "properties": {
                                       "url": {"type": "string", "required": False},
                                       "method": {"type": "string", "required": False},
                                       "status_code": {"type": "integer"},
                                       "requested_at": {"type": "string"},
                                       "log": {"type": "string", "required": False},
                                       "tests_passed": {"type": "boolean"}
                                       }
                }
