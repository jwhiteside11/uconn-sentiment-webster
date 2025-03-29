from google.cloud import datastore
from typesense_client import NewsDocument, TypesenseClient
import sys

class DatastoreClient:
    def __init__(self):
        self.client = datastore.Client()

    def newsStoryExists(self, url: str) -> bool:
        query = self.client.query(kind="newsJDWpoc")
        query.keys_only()
        query.add_filter(filter=datastore.query.PropertyFilter('url', '=', url))
        return query.fetch().num_results > 0
    
    def createNewsStoryEntity(self, news_doc: NewsDocument) -> None:
        # if news story with same url exists, don't replicate
        if self.newsStoryExists(news_doc.url):
            return
        
        story = datastore.Entity(self.client.key("newsJDWpoc", news_doc.url), exclude_from_indexes=("paragraphs",))
        story.update(news_doc.__dict__)
        self.client.put(story)

    def getNewsDocByID(self, id: str) -> NewsDocument:
        key = self.client.key("newsJDWpoc", id)
        story = self.client.get(key)
        return NewsDocument(**{pair[0]: pair[1] for pair in story.items()})

    def getAllNewsDocIDs(self, ticker: str = "") -> list[str]:
        query = self.client.query(kind="newsJDWpoc")
        query.keys_only()
        if ticker:
            query.add_filter(filter=datastore.query.PropertyFilter('ticker', '=', ticker))
        return [entity.key.id_or_name for entity in query.fetch()]
    

    def getAllNewsDocs(self, ticker: str = "") -> NewsDocument:
        ids = self.getAllNewsDocIDs(ticker)
        keys = [self.client.key("newsJDWpoc", id) for id in ids]
        stories = self.client.get_multi(keys)
        return [NewsDocument(**{pair[0]: pair[1] for pair in story.items()}) for story in stories]


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