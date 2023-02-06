import os
import copy
import time

from es import create_docs, index_doc, remove_from_index
from services.elastic import ElasticSearchConnector
from jira import download_all_issues, jira_transform


if __name__ == "__main__":
    terms_raw = download_all_issues(os.environ["JIRA_API"])
    terms = jira_transform(terms_raw)
    frontend_url = os.environ["FRONTEND_URL"]
    es_client = ElasticSearchConnector()

    internal_docs = create_docs(copy.deepcopy(terms), frontend_url, "begrep")

    remove_from_index(es_client=es_client, terms_from_jira=internal_docs)
    start = time.time()
    index_doc(internal_docs, es_client=es_client)

    end = time.time()
    print(f"Publishing {len(internal_docs)} docs, took: {end-start} seconds")
