import subprocess
import json


class DeisCkanInstanceSolr(object):

    def __init__(self, instance):
        self.instance = instance
        self.solr_spec = self.instance.spec.solrCloudCollection

    def update(self):
        self.instance.annotations.update_status('solr', 'created', lambda: self._create())

    def delete(self):
        collection_name = self.solr_spec['name']
        print(f'Deleting solrcloud collection {collection_name}')
        http_endpoint = self.instance.ckan_infra.SOLR_HTTP_ENDPOINT
        subprocess.check_call(
            f'curl -f "{http_endpoint}/admin/collections?action=DELETE&name={collection_name}"',
            shell=True
        )

    def get(self):
        solr_http_endpoint = self.instance.ckan_infra.SOLR_HTTP_ENDPOINT
        collection_name = self.instance.spec.solrCloudCollection['name']
        exitcode, output = subprocess.getstatusoutput(f'curl -s -f "{solr_http_endpoint}/{collection_name}/schema"')
        if exitcode == 0:
            res = json.loads(output)
            return {'ready': True,
                    'collection_name': collection_name,
                    'solr_http_endpoint': solr_http_endpoint,
                    'schemaVersion': res['schema']['version'],
                    'schemaName': res['schema']['name']}
        else:
            return {'ready': False,
                    'collection_name': collection_name,
                    'solr_http_endpoint': solr_http_endpoint}

    def is_ready(self):
        return 'error' not in self.get()

    def _create(self):
        collection_name = self.solr_spec['name']
        if 'configName' in self.solr_spec:
            config_name = self.solr_spec['configName']
            print(f'creating solrcloud collection {collection_name} using config {config_name}')
            http_endpoint = self.instance.ckan_infra.SOLR_HTTP_ENDPOINT
            replication_factor = self.instance.ckan_infra.SOLR_REPLICATION_FACTOR
            num_shards = self.instance.ckan_infra.SOLR_NUM_SHARDS
            subprocess.check_call(
                f'curl -f "{http_endpoint}/admin/collections?action=CREATE&name={collection_name}&collection.configName={config_name}&replicationFactor={replication_factor}&numShards={num_shards}"',
                shell=True)
        else:
            raise NotImplementedError(f'Unsupported solr cloud collection spec: {self.solr_spec}')