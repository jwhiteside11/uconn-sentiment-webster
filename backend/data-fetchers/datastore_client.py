from google.cloud import datastore
from typesense_client import CategoryNewsDocument, TypesenseClient
from fetch_earnings_calls import EarningsCallTranscript
import sys

class DatastoreClient:
    def __init__(self):
        self.client = datastore.Client()

    def entityExists(self, kind: str, id: str) -> bool:
        query = self.client.query(kind=kind)
        query.add_filter('__key__', '=', self.client.key(kind, id))
        query.keys_only() 
        res = list(query.fetch())
        return len(res) > 0
    
    def getEntityByID(self, kind: str, id: str) -> dict:
        key = self.client.key(kind, id)
        entity = self.client.get(key)
        return {pair[0]: pair[1] for pair in entity.items()}

    def getAllEntityIDsByTicker(self, kind: str, ticker: str = "") -> list[str]:
        query = self.client.query(kind=kind)
        query.keys_only()
        if ticker:
            query.add_filter(filter=datastore.query.PropertyFilter('ticker', '=', ticker))
        return [entity.key.id_or_name for entity in query.fetch()]

    def getAllEntitiesByTicker(self, kind: str, ticker: str = "") -> list[dict]:
        ids = self.getAllEntityIDsByTicker(kind, ticker)
        keys = [self.client.key(kind, id) for id in ids]
        entities = self.client.get_multi(keys)
        return [{pair[0]: pair[1] for pair in e.items()} for e in entities]
    
    def createEntityFromObject(self, kind: str, id:str, obj: object) -> None:
        # if entity with same id exists, don't replicate
        # if self.entityExists(kind, id):
        #     return
        
        entity = datastore.Entity(self.client.key(kind, id), exclude_from_indexes=("paragraphs", "keywords", "paragraph_kws"))
        entity.update(obj.__dict__)
        self.client.put(entity)

    def newsStoryExists(self, url: str) -> bool:
        return self.entityExists("newsByCategory", url)
    
    def createNewsStoryEntity(self, news_doc: CategoryNewsDocument) -> None:
        return self.createEntityFromObject("newsByCategory", news_doc.url, news_doc)

    def getNewsDocByID(self, id: str) -> CategoryNewsDocument:
        return CategoryNewsDocument(**self.getEntityByID("newsByCategory", id))

    def getAllNewsDocIDs(self, ticker: str = "") -> list[str]:
        return self.getAllEntityIDsByTicker("newsByCategory", ticker)

    def getAllNewsDocs(self, ticker: str = "") -> list[CategoryNewsDocument]:
        stories = self.getAllEntitiesByTicker("newsByCategory", ticker)
        return [CategoryNewsDocument(**story) for story in stories]

    def earningsCallExists(self, id: str) -> bool:
        return self.entityExists("callsJDWpoc", id)
    
    def createEarningsCallEntity(self, call: EarningsCallTranscript) -> None:
        return self.createEntityFromObject("callsJDWpoc", call.get_key(), call)

    def getEarningsCallByID(self, id: str) -> EarningsCallTranscript:
        return EarningsCallTranscript(**self.getEntityByID("callsJDWpoc", id))

    def getAllEarningsCallIDs(self, ticker: str = "") -> list[str]:
        return self.getAllEntityIDsByTicker("callsJDWpoc", ticker)

    def getAllEarningsCalls(self, ticker: str = "") -> list[EarningsCallTranscript]:
        calls = self.getAllEntitiesByTicker("callsJDWpoc", ticker)
        return [EarningsCallTranscript(**call) for call in calls]


def run_program():
    ticker = sys.argv[1]
    search_term = sys.argv[2]

    ds = DatastoreClient()
    ts = TypesenseClient()

    ids = ds.getAllNewsDocIDs(ticker)
    print(ids)

    for id in ids:
        new_doc = ds.getNewsDocByID(id)
        ts.createNewsDocument(new_doc)
    
def test_program():
    ds = DatastoreClient()

    ids = ds.getAllNewsDocIDs()

    # 3) Fetch entity
    docFetched = ds.getNewsDocByID("testStory")

if __name__ == "__main__":
    run_program()