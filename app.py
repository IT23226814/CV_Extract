# app.py
import streamlit as st
import pandas as pd
from database import Database
from cv_processor import CVProcessor
import json
import os

def main():
    st.title("CV Analysis and Matching System")

    # Add API key input in sidebar
    api_key = st.sidebar.text_input("Enter Google API Key", type="password")
    if not api_key:
        st.warning("Please enter your Google API Key in the sidebar to proceed")
        return

    # Set the API key as an environment variable
    os.environ['GOOGLE_API_KEY'] = api_key

    db = Database()
    try:
        cv_processor = CVProcessor()
    except ValueError as e:
        st.error(str(e))
        return

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Select Page",
        ["Upload CV", "Manage CVs", "Create Job Template", "Manage Job Templates", "Match CVs"]
    )

    if page == "Upload CV":
        st.header("Upload CV")

        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_file is not None:
            cv_text = cv_processor.extract_text_from_pdf(uploaded_file)

            if cv_text:
                parsed_data = cv_processor.parse_cv_with_genai(cv_text)

                # Show parsed data and allow editing
                st.subheader("Parsed Information")
                name = st.text_input("Name", parsed_data.get('Full Name', ''))
                email = st.text_input("Email", parsed_data.get('Email', ''))
                phone = st.text_input("Phone", parsed_data.get('Phone', ''))

                if st.button("Save to Database"):
                    db.insert_candidate(
                        name=name,
                        email=email,
                        phone=phone,
                        cv_text=cv_text,
                        parsed_data=json.dumps(parsed_data)
                    )
                    st.success("CV saved successfully!")

    elif page == "Manage CVs":
        st.header("Manage CVs")

        candidates = db.get_all_candidates()
        if candidates:
            df = pd.DataFrame(candidates,
                              columns=['ID', 'Name', 'Email', 'Phone', 'CV Text', 'Upload Date', 'Parsed Data'])
            selected_candidate = st.selectbox(
                "Select Candidate to Edit/Delete",
                df['ID'].tolist(),
                format_func=lambda x: f"{df[df['ID'] == x]['Name'].iloc[0]} ({df[df['ID'] == x]['Email'].iloc[0]})"
            )

            if selected_candidate:
                candidate = db.get_candidate(selected_candidate)
                parsed_data = json.loads(candidate[6])

                with st.form("edit_candidate"):
                    st.subheader("Edit Candidate Information")
                    name = st.text_input("Name", candidate[1])
                    email = st.text_input("Email", candidate[2])
                    phone = st.text_input("Phone", candidate[3])

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Update"):
                            if db.update_candidate(selected_candidate, name, email, phone, json.dumps(parsed_data)):
                                st.success("Candidate updated successfully!")
                            else:
                                st.error("Failed to update candidate")

                    with col2:
                        if st.form_submit_button("Delete"):
                            if db.delete_candidate(selected_candidate):
                                st.success("Candidate deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete candidate")
        else:
            st.info("No candidates in database")

    elif page == "Create Job Template":
        st.header("Create Job Template")

        title = st.text_input("Job Title")
        description = st.text_area("Job Description")
        requirements = st.text_area("Job Requirements")

        if st.button("Save Template"):
            db.insert_job_template(title, description, requirements)
            st.success("Job template saved successfully!")

    elif page == "Manage Job Templates":
        st.header("Manage Job Templates")

        templates = db.get_all_job_templates()
        if templates:
            df = pd.DataFrame(templates, columns=['ID', 'Title', 'Description', 'Requirements', 'Created Date'])
            selected_template = st.selectbox(
                "Select Template to Edit/Delete",
                df['ID'].tolist(),
                format_func=lambda x: df[df['ID'] == x]['Title'].iloc[0]
            )

            if selected_template:
                template = db.get_job_template(selected_template)

                with st.form("edit_template"):
                    st.subheader("Edit Template Information")
                    title = st.text_input("Title", template[1])
                    description = st.text_area("Description", template[2])
                    requirements = st.text_area("Requirements", template[3])

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Update"):
                            if db.update_job_template(selected_template, title, description, requirements):
                                st.success("Template updated successfully!")
                            else:
                                st.error("Failed to update template")

                    with col2:
                        if st.form_submit_button("Delete"):
                            if db.delete_job_template(selected_template):
                                st.success("Template deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete template")
        else:
            st.info("No job templates in database")

    elif page == "Match CVs":
        st.header("Match CVs to Job Requirements")

        templates = db.get_all_job_templates()
        if templates:
            template_titles = [template[1] for template in templates]
            selected_template = st.selectbox("Select Job Template", template_titles)

            if selected_template:
                template = next(t for t in templates if t[1] == selected_template)
                requirements = template[3]

                candidates = db.get_all_candidates()
                if candidates:
                    matches = []
                    for candidate in candidates:
                        parsed_data = json.loads(candidate[6])
                        score = cv_processor.match_cv_to_job(parsed_data, requirements)
                        matches.append({
                            'Name': candidate[1],
                            'Email': candidate[2],
                            'Phone': candidate[3],
                            'Match Score': score
                        })

                    matches_df = pd.DataFrame(matches)
                    top_matches = matches_df.nlargest(5, 'Match Score')

                    st.subheader("Top 5 Matching Candidates")
                    st.dataframe(top_matches)
                else:
                    st.info("No candidates in database")
        else:
            st.info("No job templates in database")


if __name__ == "__main__":
    main()