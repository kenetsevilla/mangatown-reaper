import requests
from bs4 import BeautifulSoup


class MangaTownReaper:
	def __init__(self):
		self._is_method_invalid = False

	# Download methods
	def download_chapter(self, url):
		# Error checking
		if not self.is_url_valid(url):
			return

		response = requests.get(url)

		# List all image links for each page
		print(f"\nStatus: {"OK" if response.status_code == 200 else "BAD"}")
		print(f"Total Page(s): {self.get_url_total_pages(response.url)}")

		print("Buffering images...", end="", flush=True)

		i = 1
		pages = []
		for page_num in range(self.get_url_total_pages(response.url)):
			r = requests.get(response.url + f"{i}.html")
			pages.append(BeautifulSoup(r.text, "html.parser").find_all("img", src=True))
			i += 1

		# Create a folder for images to download
		folder_name = f"Chapter {self.get_url_chapter_number(response.url)}"
		self.make_folder(folder_name)
		print(f" Created a folder '{folder_name}'")
		
		# Download all image links from each page
		total_images = 0

		for page in pages:
			for link in page:
				link = str(link)
				value = link.find("//zjcdn.mangahere.org")
				if value > -1:
					start_lnk = value
					end_lnk = link.find('jpg"') + 3
					img_lnk = f"https:{link[start_lnk:end_lnk]}"

					total_images += 1

					print(f"-> Downloading: {img_lnk}", end="  ", flush=True)

					headers = { "Referer": "https://www.mangatown.com/manga/" }
					r = requests.get(img_lnk, headers=headers)

					with open(f"{folder_name}/{total_images}.jpg", "wb") as file:
						file.write(r.content)

					print("=== Complete ===")

		print(f"\n\n[!] Chapter {int(self.get_url_chapter_number(response.url))} Complete\n")

	def download_manga(self, url):
		response = requests.get(self.get_base_url(url.rstrip("/") + "/"))

		# List all manga chapters
		links = BeautifulSoup(response.text, "html.parser").find_all("a", href=True)

		manga_name = self.get_url_manga_name(response.url)

		chapters = []
		for lnk in links:
			lnk = str(lnk)
			value = lnk.find(f"{manga_name}/c")
			if value > -1:
				if lnk.find("title=") == -1 and lnk.find("Comments</a>") == -1:
					chapters.append(self.get_url_chapter_number(lnk))

		chapters.sort()

		for c in chapters:
			url = response.url + f"c{c}/"
			print(f"\nDownloading Chapter {c}")
			self.download_chapter(url)

		print(f"\n\n[!] Manga Complete\n")

	# Interface
	def show_interface(self):
		if self.get_is_method_invalid():
			print("Invalid Method. Please enter numbers 1 or 2.",end="\n\n")

		print("Methods:")
		print("[1] Download a chapter")
		print("[2] Download a manga")

		# If method is valid, return True
		method = input("\nEnter a number: ")

		if method == "1":
			MangaTownReaper.clear_screen()
			self.print_title()

			print("\n===== Download a chapter =====\n")
			print("Chapter url example:")
			print("-> https://www.mangatown.com/manga/himouto_umaru_chan/c206/")

			self.download_chapter(input("\nEnter chapter url: "))

			MangaTownReaper.pause_interface()
			return True
		elif method == "2":
			MangaTownReaper.clear_screen()
			self.print_title()

			print("\n===== Download a manga =====\n")
			print("Manga url example:")
			print("-> https://www.mangatown.com/manga/himouto_umaru_chan/")

			self.download_manga(input("\nEnter manga url: "))

			MangaTownReaper.pause_interface()
			return True
		else:
			self.set_is_method_invalid(True)
			MangaTownReaper.clear_screen()
			return False

	def print_title(self):
		print("")                                                                                                           
		print("\t ▄▄▄     ▄▄▄                        ▄▄▄▄▄▄▄                        ▄▄▄▄▄▄")
		print("\t  ███▄ ▄███                        █▀▀██▀▀▀▀                      █▀██▀▀▀█▄")
		print("\t  ██ ▀█▀ ██         ▄        ▄▄       ██                  ▄         ██▄▄▄█▀                          ▄")
		print("\t  ██     ██   ▄▀▀█▄ ████▄ ▄████ ▄▀▀█▄ ██   ▄███▄▀█▄ █▄ ██▀████▄     ██▀▀█▄   ▄█▀█▄ ▄▀▀█▄ ████▄ ▄█▀█▄ ████▄")
		print("\t  ██     ██   ▄█▀██ ██ ██ ██ ██ ▄█▀██ ██   ██ ██ ██▄██▄██ ██ ██   ▄ ██  ██   ██▄█▀ ▄█▀██ ██ ██ ██▄█▀ ██")
		print("\t▀██▀     ▀██▄▄▀█▄██▄██ ▀█▄▀████▄▀█▄██ ▀██▄▄▀███▀  ▀██▀██▀▄██ ▀█   ▀██▀  ▀██▀▄▀█▄▄▄▄▀█▄██▄████▀▄▀█▄▄▄▄█▀")
		print("\t                             ██                                                          ██")
		print("\t                           ▀▀▀")
		print("\tv1.0.1")
		print("\tManga/Manhwa/Manhua downloader from www.mangatown.com",end="\n\n\n")

	# Getter/Setter
	def get_is_method_invalid(self):
		return self._is_method_invalid

	def set_is_method_invalid(self, _is_method_invalid):
		self._is_method_invalid = _is_method_invalid

	# Helper methods
	def get_url_total_pages(self, url):
		r = requests.get(url)
		max_page_num = 1
		pages = BeautifulSoup(r.text, "html.parser").find_all("option")
		for page in pages:
			page = str(page)
			if page.find(".html") > -1 and page.find("</option>") > -1:
				start_page = page.find(".html") + 7
				end_page = page.find(".html") + 9
				try:
					current_page_num = int(page[start_page:end_page])
					if current_page_num > max_page_num:
						max_page_num = current_page_num
				except:
					pass
		return max_page_num

	def get_url_manga_name(self, url):
		i = url.find("/manga/")
		manga_name = url[i + 7:]
		i = manga_name.find("/")

		if i > -1:
			return manga_name[:i]
		else:
			return manga_name

	def get_url_chapter_number(self, url):
		i = url.find(self.get_url_manga_name(url))
		tmp_url = url[i:].rstrip("/") + "/"
		chapter_num = tmp_url[tmp_url.find("/") + 2:] + "--"

		if len(chapter_num.rstrip("-").rstrip("/").rstrip()) < 3:
			return ""

		if chapter_num[3] == ".":
			return chapter_num[:5]
		else:
			return chapter_num[:3]

	def get_base_url(self, url):
		manga_name = self.get_url_manga_name(url)
		base_url = url[:url.find(manga_name)] + manga_name + "/"

		return base_url

	def is_url_valid(self, url):
		print(f"\nTesting: {url}",end="")
		try:
			response = requests.get(url)
		except:
			print("\n\n[!] Invalid URL.\n")
			return False

		if response.url.find("/manga/") == -1 or response.url.find("/c") == -1 or self.get_url_chapter_number(url) == "":
			print("\n\n\n[!] The URL does not appear to be a valid chapter page\n")
			return False

		return True

	@staticmethod
	def clear_screen():
		__import__("subprocess").run(
			["cmd", "/c", "cls"],
			check=False
		)

	@staticmethod
	def make_folder(folder_name: str):
		__import__("subprocess").run(
			["cmd", "/c", "mkdir", folder_name],
			check=False
		)

	@staticmethod
	def pause_interface():
		input("Press any key to continue...")


def main():
	mt_reaper = MangaTownReaper()
	mt_reaper.clear_screen()

	while (True):
		mt_reaper.print_title()
		if mt_reaper.show_interface():
			break


if __name__ == "__main__":
	while (True):
		main()