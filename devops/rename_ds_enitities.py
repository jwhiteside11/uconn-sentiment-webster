from google.cloud import datastore

# Initialize Datastore client
client = datastore.Client()

# Configuration
SOURCE_KIND = 'newsJDWpoc'
DEST_KIND = 'newsByCategory'
BATCH_SIZE = 10

def get_all_keys(kind):
    """Fetches all keys for a given kind."""
    query = client.query(kind=kind)
    query.keys_only()
    keys = [entity.key for entity in query.fetch()]
    print(f"Found {len(keys)} keys in {kind}")
    return keys

def copy_entities_by_keys(keys, source_kind, dest_kind):
    """Copies entities from source to destination kind using keys."""
    total_copied = 0

    for i in range(0, len(keys), BATCH_SIZE):
        batch_keys = keys[i:i + BATCH_SIZE]

        # Fetch full entities for this batch
        entities = client.get_multi(batch_keys)

        # Prepare new entities for destination kind
        new_entities = []
        for entity in entities:
            # Construct a new key with the same ID or name
            new_key = client.key(dest_kind, entity.key.id_or_name)

            new_entity = datastore.Entity(key=new_key, exclude_from_indexes=("paragraphs", "keywords", "paragraph_kws"))
            new_entity.update(dict(entity))
            new_entities.append(new_entity)

        # Save the copied entities
        client.put_multi(new_entities)
        total_copied += len(new_entities)
        print(f"Copied {total_copied} entities so far...")

    print(f"Finished copying {total_copied} entities from {source_kind} to {dest_kind}.")

if __name__ == '__main__':
    keys = get_all_keys(SOURCE_KIND)
    copy_entities_by_keys(keys, SOURCE_KIND, DEST_KIND)
