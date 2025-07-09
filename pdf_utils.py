import fitz
import json
import os

class toc:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.parsed_toc = []
        try:
            toc_info = self.collect_toc_info()
            self.create_nested_toc(toc_info)
        except Exception as e:
            print(f"could not parse toc from {self.pdf_path}: {e}")
    
    def collect_toc_info(self):
        """
        Collect table of contents info via get_toc() such as chapter depth, 
        chapter name and page num. Rhen enrich this with positions and ids.
        """

        doc = fitz.open(self.pdf_path)
        toc = doc.get_toc()
        doc.close()

        depths = [item[0] for item in toc]
        names = [item[1] for item in toc]
        page_numbers = [item[2] for item in toc]
        positions = self.create_chapter_positions(depths)
        ids = self.create_chapter_ids(positions)

        toc_info = zip(depths, names, page_numbers, ids, positions)

        return toc_info

    def create_chapter_positions(self, levels):
        """
        From a list of chapter levels e.g. [1,2,2] (one main chapter with two
        sub chapters), create arrays to represent the heirarchal position of 
        each chapter e.g. the first sub chapter is represented as [1,1].
        """
        total_levels = len(set(levels))

        chapter_counters = [0 for _ in range(total_levels)] # [level1, level2, level3]
        chapter_positions = []

        for level in levels:
            # Reset counters for lower levels when a higher level chapter appears
            for i in range(level, len(chapter_counters)):
                chapter_counters[i] = 0
            # Increment the counter for the current level
            chapter_counters[level - 1] += 1

            chapter_positions.append(list(chapter_counters))

        return chapter_positions

    def create_chapter_ids(self, chapter_positions):
        """
        From lists representing the heirarchal position of a chapter, create
        a chapter id e.g. position [1,2,1] will have the id "1.2.1".
        """

        chapter_ids = []
        
        for pos in chapter_positions:
            pos = list(map(str, pos))
            id = ".".join(pos)
            chapter_ids.append(id)
        
        return chapter_ids

    def create_nested_toc(self, toc_info):
        """
        Takes in a list of tuples containing chapter info and creates a list
        of dictionaries, each representing a chapter and its sub chapters.
        """

        # This list will keep track of the current path in the nested dictionary
        # It stores tuples of (depth, dictionary_reference)
        path_tracker = [] # (depth, dict_refernce)

        for depth, name, page_num, id, position in toc_info:

            current_chapter_dict = {
                "depth" : depth,
                "title" : name,
                "page_number" : page_num,
                "id" : id,
                "position" : position,
                "children": []
            }

            # Remove elements from path_tracker that are at a shallower or equal depth compared to 
            # the current chapter's depth to ensure that we're adding to the correct parent.
            while path_tracker and path_tracker[-1][0] >= depth:
                path_tracker.pop()

            if not path_tracker:
                # If path_tracker is empty, this is a top-level chapter
                self.parsed_toc.append(current_chapter_dict)

            else:
                # Add to the appropriate parent dictionary
                parent_dict = path_tracker[-1][1]
                parent_dict["children"].append(current_chapter_dict)
            
            # Add the current depth and its dictionary reference to the path tracker
            path_tracker.append((depth, current_chapter_dict))

    def save(self):
        """
        write json file to path, creates directory if needed
        """

        directory = os.path.dirname(self.pdf_path)
        toc_path = directory + "/toc.json"
        
        if os.path.exists(directory):
            pass
        else:
            os.makedirs(directory)
            print(f"created directory: {directory}")

        try:
            with open(toc_path, "w") as file:
                json.dump(self.parsed_toc, file)
            print(f"successfully wrote to: {toc_path}")
        except Exception as e:
            print(f"could not write to {toc_path}: {e}")

class doc:
    """
    Class to store and manipulate PDF's uploaded via Streamlit.file_uploader()
    """
    def __init__(self, uploaded_pdf):
        self.st_upload = uploaded_pdf
        self.bytes = self.st_upload.getvalue()
        self.name = self.st_upload.name
        self.path = f"uploaded_pdfs/{self.name}/doc.pdf"

    def save(self):
        """
        write pdf file to path, creates directory if needed
        """

        path = self.path
        directory = os.path.dirname(path)

        if os.path.exists(directory):
            pass
        else:
            os.makedirs(directory)
            print(f"created directory: {directory}")

        try:
            with open(path, "wb") as file:
                file.write(self.bytes)
            print(f"successfully wrote to: {path}")
        except Exception as e:
            print(f"could not write to {path}: {e}")

# sample usage
# pdf_path = "uploaded_pdfs/Prompt Engineering_v7/doc.pdf"
# pdf = toc(pdf_path)
# pdf.save()
