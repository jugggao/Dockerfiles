ARG elasticsearch_version=7.17.3
FROM docker.elastic.co/elasticsearch/elasticsearch:${elasticsearch_version}

ENV elasticsearch_version=7.17.3
RUN bin/elasticsearch-plugin install -b https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v${elasticsearch_version}/elasticsearch-analysis-ik-${elasticsearch_version}.zip
