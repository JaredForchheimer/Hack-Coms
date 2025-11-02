import sys
from process import (
    scrape,
    parse,
    summarize,
    translate,
    load_storage,
    save_storage,
)


def main():
    try:
        # Load persistent storage
        storage = load_storage()
    except Exception as e:
        print(f"Error loading storage file: {e}")
        storage = {}

    # This list is a temporary, in-memory queue for the current session
    sources_to_process = []

    # Get a set of URLs that are already processed and stored
    processed_urls = set(storage.keys())

    while True:
        print("\n--- Content Processor Menu ---")
        print("1. Add a new URL to the processing queue")
        print("2. Process a URL from the queue")
        print("3. View stored summaries")
        print("4. Exit")
        choice = input("Select an option: ").strip()

        if choice == "1":
            new_url = input("Enter a new URL: ").strip()
            if not new_url:
                continue

            if new_url in processed_urls:
                print("This URL has already been processed and stored.")
            elif new_url in sources_to_process:
                print("This URL is already in the queue.")
            else:
                sources_to_process.append(new_url)
                print(f"URL added to queue: {new_url}")

        elif choice == "2":
            if not sources_to_process:
                print("Processing queue is empty. Add a URL first.")
                continue

            print("\nAvailable URLs to process:")
            for idx, src in enumerate(sources_to_process):
                print(f"{idx + 1}. {src}")

            sel = input("Select a source number to process: ").strip()
            try:
                sel_idx = int(sel) - 1
                if not 0 <= sel_idx < len(sources_to_process):
                    raise IndexError

                url_to_process = sources_to_process[sel_idx]

            except (ValueError, IndexError):
                print("Invalid selection.")
                continue

            try:
                # 1. Scrape
                content = scrape(url_to_process)
                if content.startswith("Error:"):
                    raise ValueError(content)

                # 2. Parse (Moderate)
                # Note: parse() will raise ValueError if moderation fails
                safe_content = parse(content)

                # 3. Summarize
                content_summary = summarize(safe_content)
                print("\n✅ Summary:")
                print(content_summary)

                # 4. Ask to translate
                trans_lang = input(
                    "\nEnter a language to translate the SUMMARY to (e.g., 'Spanish', or leave empty to skip): "
                ).strip()

                translated_summary = None
                if trans_lang:
                    # Translate the SUMMARY, not the full content
                    translated_summary = translate(content_summary, trans_lang)
                    print(f"\n✅ Translated to {trans_lang}:")
                    print(translated_summary)

                # 5. Store results
                storage[url_to_process] = {
                    "summary": content_summary,
                    # We don't store the full 'safe_content' as it could be huge
                }
                if translated_summary:
                    storage[url_to_process]["translation"] = translated_summary
                    storage[url_to_process]["translation_lang"] = trans_lang

                save_storage(storage)
                print(
                    f"\nSuccessfully processed and saved summary for: {url_to_process}"
                )

                # 6. Remove from queue and add to processed set
                sources_to_process.pop(sel_idx)
                processed_urls.add(url_to_process)

            except Exception as e:
                print(
                    f"\nError processing URL '{url_to_process}': {str(e)}",
                    file=sys.stderr,
                )
                # Optionally, you could remove it from the list even if it fails
                # sources_to_process.pop(sel_idx)

        elif choice == "3":
            if not storage:
                print("\nNo stored content. Process some URLs first.")
                continue

            print("\n--- Stored Summaries ---")
            for url, data in storage.items():
                print(f"\n🔗 URL: {url}")
                print(f"📄 Summary:\n{data.get('summary', 'N/A')}")

                if data.get("translation"):
                    lang = data.get("translation_lang", "translated")
                    print(
                        f"\n🌐 {lang.capitalize()} Translation:\n{data.get('translation')}"
                    )
                print("-" * 20)

        elif choice == "4":
            print("Exiting.")
            sys.exit(0)

        else:
            print("Invalid option, please try again.")


if __name__ == "__main__":
    main()
