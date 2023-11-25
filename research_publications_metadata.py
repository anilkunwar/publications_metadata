import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import base64
from io import BytesIO

# Function to render multiline text in PDF
def render_multiline_text(pdf, text, x, y, max_line_length=50):
    lines = []
    for i in range(0, len(text), max_line_length):
        lines.append(text[i:i + max_line_length])

    for idx, line in enumerate(lines):
        pdf.drawString(x, y - (idx * 20), line)

# Updated PDF Generation Function
def generate_pdf(researcher_name, project_name, join_date, fill_date, publications):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    pdf.setTitle("Research Dissemination Metadata")
    pdf.drawString(100, 750, "Research Logbook")
    pdf.drawString(100, 730, f"Researcher's Name: {researcher_name}")
    pdf.drawString(100, 710, f"Project: {project_name}")
    pdf.drawString(100, 690, f"Joining Date: {join_date.strftime('%Y-%m-%d')}")
    pdf.drawString(100, 670, f"Form Filling Date: {fill_date.strftime('%Y-%m-%d')}")

    y_position = 650
    for idx, publication in enumerate(publications, start=1):
        pdf.drawString(100, y_position, f"Publication {idx}")
        author_text = publication.get('Author Names', '')
        title_text = publication.get('Title', '')

        # Render Author Names
        pdf.drawString(100, y_position - 20, "Author Names:")
        render_multiline_text(pdf, author_text, 120, y_position - 40)  # Render Author Names
        
        # Adjust y_position based on the number of lines in Author Names
        num_author_lines = len(author_text) // 50 + 1 if author_text else 1
        y_position -= (num_author_lines * 20 + 40)

        # Render Title
        pdf.drawString(100, y_position, "Title:")
        render_multiline_text(pdf, title_text, 120, y_position - 20)  # Render Title
        
        # Adjust y_position based on the number of lines in Title
        num_title_lines = len(title_text) // 50 + 1 if title_text else 1
        y_position -= (num_title_lines * 20 + 40)

        # Render other fields
        pdf.drawString(100, y_position - 20, f"Journal Name: {publication.get('Journal Name', '')}")
        pdf.drawString(100, y_position - 40, f"Volume: {publication.get('Volume', '')}")
        pdf.drawString(100, y_position - 60, f"Year: {publication.get('Year', '')}")
        pdf.drawString(100, y_position - 80, f"Article Number: {publication.get('Article Number', '')}")
        pdf.drawString(100, y_position - 100, f"DOI: {publication.get('DOI', '')}")
        pdf.drawString(100, y_position - 120, f"Impact Factor (Current): {publication.get('Impact Factor', '')}")
        #pdf.drawString(100, y_position - 140, f"Open Access Link: {publication.get('Open Access Link', '')}")
        # Render Open Access Links
        open_access_links = publication.get('Open Access Link', [])
        if open_access_links:
            pdf.drawString(100, y_position - 160, "Open Access Links:")
            link_y_position = y_position - 180
            for link in open_access_links:
                pdf.drawString(120, link_y_position, link)  # Render each link on a new line
                link_y_position -= 20  # Adjust position for the next link

        # Adjust y_position based on the number of lines in Open Access Links
        num_link_lines = len(open_access_links)
        y_position -= (max(1, num_link_lines) * 20 + 60)  # Ensure at least one line space after the links

        #data_code_links = '|'.join(publication.get('Data and Codes Links', []))
        #pdf.drawString(100, y_position - 160, f"Data and Codes Links: {data_code_links}")
        # Render Data and Codes Links
        data_links = publication.get('Data and Codes Links', [])
        if data_links:
            pdf.drawString(100, y_position - 180, "Data and Codes Links:")
            link_y_position = y_position - 200
            for link in data_links:
                render_multiline_text(pdf, link, 120, link_y_position)  # Render each link on a new line
                link_y_position -= 20  # Adjust position for the next link

        # Adjust y_position based on the number of lines in Data and Codes Links
        num_link_lines = sum((len(link.split()) // 50 + 1) for link in data_links)
        y_position -= (max(1, num_link_lines) * 20 + 40)  # Ensure at least one line space after the links
        
        y_position -= 200  # Adjust the position for the next entry

    pdf.save()
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes




# Function to generate CSV
def generate_csv(researcher_name, project_name, join_date, fill_date, publications):
    data = {
        'Researcher Name': [],
        'Project Name': [],
        'Join Date': [],
        'Fill Date': [],
        'Author Names': [],
        'Title': [],
        'Journal Name': [],
        'Volume': [],
        'Year': [],
        'Article Number': [],
        'DOI': [],
        'Impact Factor (Current)': [],
        'Open Access Link': [],
        'Data and Codes Links': []
    }

    for publication in publications:
        data['Researcher Name'].append(researcher_name)
        data['Project Name'].append(project_name)
        data['Join Date'].append(join_date.strftime('%Y-%m-%d'))
        data['Fill Date'].append(fill_date.strftime('%Y-%m-%d'))
        data['Author Names'].append(publication.get('Author Names', ''))
        data['Title'].append(publication.get('Title', ''))
        data['Journal Name'].append(publication.get('Journal Name', ''))
        data['Volume'].append(publication.get('Volume', ''))
        data['Year'].append(publication.get('Year', ''))
        data['Article Number'].append(publication.get('Article Number', ''))
        data['DOI'].append(publication.get('DOI', ''))
        data['Impact Factor (Current)'].append(publication.get('Impact Factor', ''))
        #data['Open Access Link'].append(publication.get('Open Access Link', ''))
        # Add multiple open access links with '|' separator
        #open_access_links = publication.get('Open Access Link', '').split('|')
        #data['Open Access Link'].append('|'.join(open_access_links))
        # Join multiple links as a single string with separator '|' and add to the data
        data['Open Access Link'].append('|'.join(publication.get('Open Access Link', [])))

        # Join multiple links as a single string with separator '|' and add to the data
        data['Data and Codes Links'].append('|'.join(publication.get('Data and Codes Links', [])))

    # Ensure all arrays have the same length by filling missing values with empty strings
    max_length = max(len(arr) for arr in data.values())
    for key in data:
        data[key] += [''] * (max_length - len(data[key]))

    df = pd.DataFrame(data)
    return df


# Main function
def main():
    st.title("Research Dissemination Logbook")

    researcher_name = st.text_input("Researcher's Name")
    project_name = st.text_input("Project Name")
    join_date = st.date_input("Joining Date")
    fill_date = st.date_input("Form Filling Date")
    
    publications = []
    num_publications = st.number_input("Number of Publications", min_value=1, step=1)
    
    #   i starts from 0
    for i in range(num_publications):
        st.sidebar.markdown(f"### Publication {i + 1}")
        author_names = st.sidebar.text_input(f"Author Names_{i+1}")
        title = st.sidebar.text_input(f"Title_{i+1}")
        journal_name = st.sidebar.text_input(f"Journal Name_{i+1}")
        volume = st.sidebar.text_input(f"Volume_{i+1}")
        year = st.sidebar.text_input(f"Year_{i+1}")
        article_number = st.sidebar.text_input(f"Article Number_{i+1}")
        doi = st.sidebar.text_input(f"DOI_{i+1}")
        impact_factor = st.sidebar.text_input(f"Impact Factor (Current)_{i+1}")
        #open_access_link = st.sidebar.text_input(f"Link to Open Access Full text_{i+1}")
        num_open_access_links = st.sidebar.number_input(f"Number of Links for Open Access Publications_{i+1}", min_value=0, step=1)
        open_access_links = [st.sidebar.text_input(f"Link OA Publications {j + 1}_{i+1}") for j in range(num_open_access_links)]

        num_data_codes_links = st.sidebar.number_input(f"Number of Links for Data and Codes_{i+1}", min_value=0, step=1)
        data_code_links = [st.sidebar.text_input(f"Link data codes {j + 1}_{i+1}") for j in range(num_data_codes_links)]

        publication = {
            'Author Names': author_names,
            'Title': title,
            'Journal Name': journal_name,
            'Volume': volume,
            'Year': year,
            'Article Number': article_number,
            'DOI': doi,
            'Impact Factor': impact_factor,
            'Open Access Link': open_access_links,
            'Data and Codes Links': data_code_links
        }
        publications.append(publication)

    if st.button("Generate Files"):
        if not (researcher_name and project_name and join_date and fill_date and publications):
            st.error("Please fill in all the required fields.")
        else:
            # Generate PDF
            pdf_bytes = generate_pdf(researcher_name, project_name, join_date, fill_date, publications)
            if pdf_bytes:
                b64_pdf = base64.b64encode(pdf_bytes).decode()
                href_pdf = f'<a href="data:application/pdf;base64,{b64_pdf}" download="research_logbook.pdf">Download PDF</a>'
                st.markdown(href_pdf, unsafe_allow_html=True)

            # Generate CSV
            df = generate_csv(researcher_name, project_name, join_date, fill_date, publications)
            csv = df.to_csv(index=False)
            b64_csv = base64.b64encode(csv.encode()).decode()
            href_csv = f'<a href="data:text/csv;base64,{b64_csv}" download="research_logbook.csv">Download CSV</a>'
            st.markdown(href_csv, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

