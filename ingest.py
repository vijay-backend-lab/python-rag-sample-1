import argparse
from dotenv import load_dotenv
from rag_app.config import Settings
from rag_app.ingestion import ThirdPartyIngestionService

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Embed and bulk-index third-party documents")
    parser.add_argument("--batch-size", type=int, default=100)
    args = parser.parse_args()
    result = ThirdPartyIngestionService.from_settings(Settings.from_env(), args.batch_size).run()
    print(result)
    if result["failed"]: raise SystemExit(1)

if __name__ == "__main__":
    main()
