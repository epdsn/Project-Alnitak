#!/usr/bin/env python3
"""
Command-line interface for ingesting documents into the Alnitak RAG system.
"""

import argparse
import sys
import os
from ingest import DocumentIngester, ingest_documents
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(
        description="Ingest documents into the Alnitak RAG system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest a single file
  python ingest_cli.py --file document.pdf
  
  # Ingest multiple files
  python ingest_cli.py --file doc1.txt --file doc2.md --file doc3.pdf
  
  # Ingest all supported files from a directory
  python ingest_cli.py --directory ./documents
  
  # Ingest specific file types from a directory
  python ingest_cli.py --directory ./documents --extensions .txt .md
  
  # Reset the collection before ingesting
  python ingest_cli.py --reset --directory ./documents
  
  # Show collection info
  python ingest_cli.py --info
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        action='append',
        help='File(s) to ingest (can be specified multiple times)'
    )
    
    parser.add_argument(
        '--directory', '-d',
        help='Directory to ingest all supported files from'
    )
    
    parser.add_argument(
        '--extensions',
        nargs='+',
        default=['.txt', '.md', '.markdown', '.pdf'],
        help='File extensions to process when using --directory (default: .txt .md .markdown .pdf)'
    )
    
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset the collection before ingesting (delete all existing documents)'
    )
    
    parser.add_argument(
        '--info',
        action='store_true',
        help='Show information about the current collection'
    )
    
    parser.add_argument(
        '--persist-dir',
        default='./chroma_db',
        help='Directory to persist ChromaDB data (default: ./chroma_db)'
    )
    
    args = parser.parse_args()
    
    # Show collection info if requested
    if args.info:
        ingester = DocumentIngester(args.persist_dir)
        info = ingester.get_collection_info()
        print("\n📊 Collection Information:")
        for key, value in info.items():
            print(f"  {key}: {value}")
        return
    
    # Validate arguments
    if not args.file and not args.directory:
        print("❌ Error: You must specify either --file or --directory")
        parser.print_help()
        sys.exit(1)
    
    # Initialize ingester
    ingester = DocumentIngester(args.persist_dir)
    
    # Reset collection if requested
    if args.reset:
        print("🗑️  Resetting collection...")
        ingester.reset_collection()
        print("✅ Collection reset successfully")
    
    total_chunks = 0
    
    # Ingest individual files
    if args.file:
        print(f"\n📁 Processing {len(args.file)} file(s)...")
        for file_path in args.file:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                continue
            
            try:
                chunks = ingester.ingest_file(file_path)
                total_chunks += chunks
                print(f"✅ Ingested {chunks} chunks from {file_path}")
            except Exception as e:
                print(f"❌ Failed to ingest {file_path}: {e}")
    
    # Ingest directory
    if args.directory:
        if not os.path.exists(args.directory):
            print(f"❌ Directory not found: {args.directory}")
            sys.exit(1)
        
        print(f"\n📂 Processing directory: {args.directory}")
        print(f"📋 File extensions: {', '.join(args.extensions)}")
        
        try:
            results = ingester.ingest_directory(args.directory, args.extensions)
            
            successful_files = 0
            for file_path, chunks in results.items():
                if chunks > 0:
                    print(f"✅ {file_path}: {chunks} chunks")
                    total_chunks += chunks
                    successful_files += 1
                else:
                    print(f"❌ {file_path}: failed")
            
            print(f"\n📈 Summary: {successful_files} files processed, {total_chunks} total chunks")
            
        except Exception as e:
            print(f"❌ Error processing directory: {e}")
            sys.exit(1)
    
    # Show final collection info
    if total_chunks > 0:
        print(f"\n🎉 Ingestion complete! Total chunks added: {total_chunks}")
        info = ingester.get_collection_info()
        print(f"📊 Total documents in collection: {info['total_documents']}")

if __name__ == '__main__':
    main()
