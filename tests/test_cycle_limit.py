import main
from config import MAX_COMMENTS_PER_CYCLE

class FakeAuthor:
    def __init__(self, name):
        self.name = name

class FakeComment:
    def __init__(self, comment_id):
        self.id = comment_id
        self.author = FakeAuthor("test-user")
        self.body = "ordinary text"

def test_cycle_limit_is_independent_of_duplicate_cache(monkeypatch):
    main.recent_comment_ids.clear()
    for i in range(500):
        main.recent_comment_ids.append(f"old-{i}")

    handled = []
    monkeypatch.setattr(main, "handle_comment", lambda comment: handled.append(comment.id))

    comments = [FakeComment(f"new-{i}") for i in range(MAX_COMMENTS_PER_CYCLE + 10)]
    processed = main.process_comment_cycle(comments)

    assert processed == MAX_COMMENTS_PER_CYCLE
    assert len(handled) == MAX_COMMENTS_PER_CYCLE
    assert handled[0] == "new-0"
