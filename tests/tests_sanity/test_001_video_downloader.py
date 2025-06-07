from resources.buscar_clips import VideoDownloader

def test_single_query():
    video_downloader = VideoDownloader(debug=True)  # Activar mensajes de depuración en la consola
    found = video_downloader.query(name="stars", count=2)
    print(f"[{len(found)}] - {found}")

    assert len(found) == 2, "2 Elementos"

def test_multiple_queries():
    video_downloader = VideoDownloader(debug=True)  # Activar mensajes de depuración en la consola
    queries = ["space", "stars", "food", "healthy", "safety", "stressed"]

    videos_found_dict = dict()
    for query in queries:
        videos_found = video_downloader.query(name=query, count=5)

        print(f"[{len(videos_found)}] - {query} {videos_found}")
        videos_found_dict.update(dict({
            query: videos_found
        }))
