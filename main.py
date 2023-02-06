import os
import copy
import time

if __name__ == "__main__":
    teamcat_url = os.environ["TEAMKATALOG_URL"]

    internal_docs = create_docs(copy.deepcopy(terms), teamcat_url, "XXX")

    remove_from_index(es_client=es_client, terms_from_jira=internal_docs)
    start = time.time()
    index_doc(internal_docs, es_client=es_client)

    end = time.time()
    print(f"Publishing {len(internal_docs)} docs, took: {end-start} seconds")
