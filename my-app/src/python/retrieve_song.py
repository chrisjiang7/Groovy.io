from Ai_DJ_DB import retrieve_audio_from_mongodb, list_stored_files

# List all stored songs
print("Available songs in MongoDB:")
stored_files = list_stored_files()
for i, file in enumerate(stored_files, 1):
    print(f"{i}. {file['filename']} (stored on {file['stored_date']})")

if stored_files:
    try:
        choice = int(input("\nEnter the number of the song you want to retrieve (1, 2, etc.): "))
        if 1 <= choice <= len(stored_files):
            filename = stored_files[choice-1]['filename']
            output_name = f"retrieved_{filename}"
            print(f"\nRetrieving {filename} from MongoDB...")
            retrieve_audio_from_mongodb(filename, output_name)
            print(f"Done! Check '{output_name}' in your current directory.")
        else:
            print("Invalid choice!")
    except ValueError:
        print("Please enter a valid number!")
else:
    print("No songs found in the database.") 
