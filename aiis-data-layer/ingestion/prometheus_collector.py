import yaml
import logging
import datetime
from typing import List, Dict, Any
from prometheus_api_client import PrometheusConnect

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PrometheusCollector:
    def __init__(self, config_path: str = "configs/metrics.yaml", prometheus_url: str = "http://localhost:9090"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.prom = PrometheusConnect(url=prometheus_url, disable_ssl=True)
        self.metrics_conf = self.config['metrics']

    def _query(self, query: str) -> List[Dict[str, Any]]:
        try:
            result = self.prom.custom_query(query=query)
            return result
        except Exception as e:
            logger.error(f"Error querying Prometheus: {e}")
            return []

    def get_cpu_usage(self) -> List[Dict[str, Any]]:
        return self._query(self.metrics_conf['cpu']['query'])

    def get_memory_usage(self) -> List[Dict[str, Any]]:
        return self._query(self.metrics_conf['memory']['query'])

    def get_network_usage(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "rx": self._query(self.metrics_conf['network_rx']['query']),
            "tx": self._query(self.metrics_conf['network_tx']['query'])
        }

    def get_replica_count(self) -> List[Dict[str, Any]]:
        return self._query(self.metrics_conf['replicas']['query'])

    def get_node_metrics(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "cpu": self._query(self.metrics_conf['node_cpu']['query']),
            "memory": self._query(self.metrics_conf['node_memory']['query'])
        }

    def collect_all(self, cluster_id: str = "prod-01") -> List[Dict[str, Any]]:
        """
        Aggregates metrics into the required JSON format.
        This is a simplified version that merges metrics by pod/namespace.
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        cpu_data = self.get_cpu_usage()
        mem_data = self.get_memory_usage()
        replica_data = self.get_replica_count()
        
        # Mapping pod/namespace to metrics
        records = {}

        for entry in cpu_data:
            metric = entry['metric']
            pod = metric.get('pod', 'unknown')
            namespace = metric.get('namespace', 'default')
            key = (pod, namespace)
            if key not in records:
                records[key] = {
                    "timestamp": timestamp,
                    "cluster_id": cluster_id,
                    "pod": pod,
                    "namespace": namespace,
                    "cpu": 0.0,
                    "memory": 0.0,
                    "replicas": 0
                }
            records[key]["cpu"] = float(entry['value'][1])

        for entry in mem_data:
            metric = entry['metric']
            pod = metric.get('pod', 'unknown')
            namespace = metric.get('namespace', 'default')
            key = (pod, namespace)
            if key in records:
                records[key]["memory"] = float(entry['value'][1]) / (1024 * 1024) # MB

        for entry in replica_data:
            metric = entry['metric']
            deployment = metric.get('deployment', 'unknown')
            namespace = metric.get('namespace', 'default')
            # For simplicity, we might associate replicas with pods in that namespace or keep it separate
            # The requirement suggests a record with replicas. We'll find a matched namespace.
            for key, val in records.items():
                if val['namespace'] == namespace:
                    val['replicas'] = int(entry['value'][1])

        return list(records.values())

if __name__ == "__main__":
    collector = PrometheusCollector()
    # Example usage
    # print(collector.collect_all())
