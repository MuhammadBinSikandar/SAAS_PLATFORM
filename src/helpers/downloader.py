import requests
from pathlib import Path

def download_to_local(url : str, out_path : Path, parent_makedir:bool=True):
    if not isinstance(out_path, Path):
        raise ValueError(f'{out_path} must be a valid pathlib.Path object')
    if parent_makedir:
        out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        response = requests.get(url)
        response.raise_for_status()
        out_path.write_bytes(response.content)
        return True
    except requests.RequestException as e:
        print(f'Failed to donwload {url}: {e}')
        return False


# Below is the code in case the .map file is not available for download.
# import requests
# from pathlib import Path

# def download_to_local(url: str, out_path: Path, parent_makedir: bool = True):
#     if not isinstance(out_path, Path):
#         raise ValueError(f'{out_path} must be a valid pathlib.Path object')
#     if parent_makedir:
#         out_path.parent.mkdir(parents=True, exist_ok=True)
#     try:
#         response = requests.get(url)
#         response.raise_for_status()
        
#         # Decode the content as text to check and remove the source map line
#         content = response.text
        
#         # Remove the unwanted source map line if it exists
#         content = content.replace('//# sourceMappingURL=flowbite.min.js.map', '')
        
#         # Write the content back to the file
#         out_path.write_text(content, encoding='utf-8')
#         return True
#     except requests.RequestException as e:
#         print(f'Failed to download {url}: {e}')
#         return False
