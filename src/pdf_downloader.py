import requests
import os
def download_pdf(paper_id):
    url = f"https://arxiv.org/pdf/{paper_id}.pdf"

    #Create directory if it doesn't exist
    save_dir = "data/papers"
    os.makedirs(save_dir, exist_ok=True)

    #define file path
    file_path = os.path.join(save_dir, f"{paper_id}.pdf")

    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"PDF downloaded successfully as {file_path}")
        return file_path
        
    else:
        print(f"Failed to download PDF. Status code: {response.status_code}")
        return None

