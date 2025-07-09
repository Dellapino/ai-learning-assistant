import streamlit as st

st.title('My First Streamlit App')
number = st.slider('Select a number', 0, 100)
st.write('You selected:', number)


def select_pdf():
    """Presents a list of available PDF files and prompts the user to select one.

    Returns:
        str: The full path to the selected PDF file.
    """
    dataset_path = "/kaggle/input/google-gen-ai-intensive-whitepapers"
    pdf_list = os.listdir(dataset_path)
    print("Select a Gen AI Whitepaper to study:\n")
    for i, pdf in enumerate(pdf_list):
        print(f"""\t{i+1} - {pdf}""")

    completed_input = False
    while not completed_input:
        try:
            selected_pdf = int(input("\n\tSelection: ")) - 1
            if selected_pdf >= 0 and selected_pdf < len(pdf_list):
                completed_input = True
            else:
                print("\tSelect a valid option.")
        except:
            print("\tEnter an Integer.")

    pdf_path = dataset_path + "/" + pdf_list[selected_pdf]
    return pdf_path

def select_chapter(toc):
    """Presents a hierarchical list of chapters to the user and prompts for selection.

    Args:
        toc (list[dict]): A list of dictionaries representing the table of contents,
                          including chapter names and their hierarchical levels.

    Returns:
        list[dict]: A list of dictionaries representing the selected chapter(s)
                    (can be a main chapter or a sub-section).
    """

    print("\nLets start studying! Pick a chapter to continue.\n")

    chapter_count = 0
    for chapter in toc:
        if chapter['chapter_level_1'] == 0 and chapter['chapter_level_2'] == 0:
            print(f"\t{chapter['chapter_level_0']} - {chapter['chapter_name']}")
            chapter_count += 1
    
    completed_input = False
    while not completed_input:
        try:
            primary_selection = int(input("\n\tSelection: "))
            if primary_selection > 0 and primary_selection <= chapter_count:
                completed_input = True
            else:
                print("\tSelect a valid option.")
        except:
            print("\tEnter an Integer.")
    
    # selected_chapters
    primary_chapters = []
    for chapter in toc:
        if chapter['chapter_level_0'] == primary_selection:
            primary_chapters.append(chapter)
    
    
    if len(primary_chapters) > 1:
        print("\nThis is a big chapter, lets break it down! Pick a section to continue.\n")
        print(f"\t{primary_chapters[0]['chapter_level_0']} - {primary_chapters[0]['chapter_name']}")

        section_count = 0
        for chapter in primary_chapters:
            if chapter['chapter_level_1'] != 0 and chapter['chapter_level_2'] == 0:
                print(f"\t\t{chapter['chapter_level_1']} - {chapter['chapter_name']}")
                section_count += 1

        completed_input = False
        while not completed_input:
            try:
                secondary_selection = int(input("\n\t\tSelection: "))
                if secondary_selection > 0 and secondary_selection <= section_count:
                    completed_input = True
                else:
                    print("\t\tSelect a valid option.")
            except:
                print("\t\tEnter an Integer.")
    
        secondary_chapters = []
        for chapter in primary_chapters:
            if chapter['chapter_level_1'] == secondary_selection:
                secondary_chapters.append(chapter)
    else:
        secondary_chapters = primary_chapters

    return secondary_chapters

# create interface to go to the next section.

def select_path():
    """Presents options for the user to choose the next action.

    Returns:
        int: The number corresponding to the user's selection.
    """

    paths = ["Quiz Mode", "Chapter Selector", "Finish Studying"]
    
    print("Hi again! What would you like to do next?\n")
    
    for i, path in enumerate(paths):
        print(f"\t{i+1} - {path}")

    completed_input = False
    while not completed_input:
        try:
            selected_path = int(input("\n\tSelection: "))
            if selected_path > 0 and selected_path <= len(paths):
                completed_input = True
            else:
                print("\tSelect a valid option.")
        except:
            print("\tEnter an Integer.")

    return selected_path


def test_understanding(selected_chapters):
    """Initiates the quiz mode to test the user's understanding of the selected chapter sections.

    Generates questions, collects user answers, and reviews them.

    Args:
        selected_chapters (list[dict]): A list of dictionaries representing the
                                         selected chapter sections.
    """
    model_questions = create_model_questions(selected_chapters)
    clear_output()
    display(Markdown("""**< AI Learning Assistant >**"""))
    display(Markdown(f"""
***
**Quiz Start**
***
    """))
    answered_questions = collect_user_answers(model_questions)
    review_user_answers(selected_chapters, answered_questions)
    display(Markdown(f"""
***
**Quiz Complete**
***
    """))


# collect user answers

def collect_user_answers(qas):
    """Presents a list of questions to the user and collects their answers.

    Args:
        qas (list[dict]): A list of dictionaries, where each dictionary contains
                          a "question_number" and a "question".

    Returns:
        list[dict]: The input list of dictionaries, with an additional "user_answer"
                    key-value pair for each question.
    """
    for qa in qas:
        print(f"""\nQuestion {qa["question_number"]}: {qa["question"]}""")
        qa["user_answer"] = input("Answer: ")
    return qas




def display_quiz_outcome():
    print("Review complete!")

    total = 0
    total_correct = 0
    for answer in reviewed_answers:
        total += 1
        outcome = 'Incorrect'
        if answer['correct']:
            total_correct += 1
            outcome = 'Correct'
        
        print(f"""\nQuestion {answer['question_number']} review: {outcome}\nReason: {answer['reason']}\nModel answer: {qas[answer['question_number']-1]['model_answer']}""")
    
    print(f"""\nScore: {total_correct}/{total}""")



# display(Markdown("""**< AI Learning Assistant >**"""))

# initial set up
pdf_path = select_pdf()

print("\nAccessing pdf content ...")
sample_pdf = client.files.upload(file="/kaggle/input/google-gen-ai-intensive-whitepapers/Foundational Large Language models and text generation_v2.pdf")
selected_pdf = client.files.upload(file=pdf_path)
print("Got pdf content!")

print("\nParsing table of contents ...")
toc_pages = find_toc_pages()
chapters, indents = extract_toc_data(pdf_path, toc_pages["page_numbers"])
toc_chapters = extract_chapter_name_number(chapters)
toc_positions = pdf_indents_to_chapter_hierarchy(indents)

if len(toc_chapters) == len(toc_positions):
    toc = []
    for i in range(len(toc_chapters)):
        toc.append(toc_chapters[i] | toc_positions[i])
else:
    raise Exception("Mismatch in count of chapter names and chapter positions")
print("Parsing complete!")

# this is the main looooooop.

selected_path = 2

while selected_path !=3:

    if selected_path == 1:
        test_understanding(selected_chapters)
    elif selected_path == 2:
        selected_chapters = select_chapter(toc)
        explain_section(selected_chapters)
    else:
        print("\nUh oh ...")

    selected_path = select_path()

print("\nGoodbye, see you again!")
display(Markdown("""**< AI Learning Assistant >**"""))