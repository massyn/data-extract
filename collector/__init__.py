import os
import json
import datetime
import uuid
import boto3

class Collector:
    def __init__(self):
        print('collector class init')

    def log(self,i,t):
        print(f"[collector] ({__name__}) - {i} - {t}")
        if i == 'FATAL':
            exit(1)

    def check_inputs(self,mappings,**KW):
        data = {}
        for m in mappings:
            if m not in KW:
                if mappings[m] is None:
                    self.log('FATAL',f"Mapping {m} is missing - cannot continue")
                else:
                    self.log('WARN',f"Mapping {m} is missing - setting default {mappings[m]}")
                data[m] = mappings[m]
            else:
                self.log('INFO',f"Mapping {m}")
                data[m] = KW[m]
        self.log('INFO','Inputs have been defined')
        return data
