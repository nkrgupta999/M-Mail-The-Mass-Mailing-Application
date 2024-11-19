import streamlit as st

def gmail_template():
    # Initialize session state variables for Gmail templates
    if 'gmail_templates' not in st.session_state:
        st.session_state['gmail_templates'] = {}
    if 'selected_gmail_template' not in st.session_state:
        st.session_state['selected_gmail_template'] = None

    st.title("Gmail Email Templates Manager")

    # Form for creating or updating templates
    with st.form("gmail_template_form"):
        template_name = st.text_input("Template Name", 
                                      value=(st.session_state['selected_gmail_template']['name']
                                             if st.session_state['selected_gmail_template'] else ""))
        subject = st.text_input("Email Subject", 
                                 value=(st.session_state['selected_gmail_template']['subject']
                                        if st.session_state['selected_gmail_template'] else ""))
        body = st.text_area("Email Body", 
                            value=(st.session_state['selected_gmail_template']['body']
                                   if st.session_state['selected_gmail_template'] else ""))
        attachment = st.file_uploader("Attach a document (PDF, Image, etc.)", type=['pdf', 'png', 'jpg', 'jpeg', 'docx'])

        action = st.radio("Action", ['Create', 'Update'])
        submit_button = st.form_submit_button("Submit")

    if submit_button:
        if not template_name or not subject or not body:
            st.error("All fields are required!")
        elif action == "Create":
            if template_name in st.session_state['gmail_templates']:
                st.error(f"Template '{template_name}' already exists!")
            else:
                st.session_state['gmail_templates'][template_name] = {
                    "subject": subject,
                    "body": body,
                    "attachment": attachment.name if attachment else None
                }
                st.success(f"Template '{template_name}' created successfully!")
        elif action == "Update":
            if template_name not in st.session_state['gmail_templates']:
                st.error(f"Template '{template_name}' does not exist!")
            else:
                st.session_state['gmail_templates'][template_name] = {
                    "subject": subject,
                    "body": body,
                    "attachment": attachment.name if attachment else st.session_state['gmail_templates'][template_name]["attachment"]
                }
                st.success(f"Template '{template_name}' updated successfully!")

    st.subheader("Existing Gmail Templates")
    if st.session_state['gmail_templates']:
        for idx, (name, template) in enumerate(st.session_state['gmail_templates'].items()):
            st.write(f"**Template Name**: {name}")
            st.write(f"**Subject**: {template['subject']}")
            st.write(f"**Body**: {template['body']}")
            st.write(f"**Attachment**: {template['attachment'] or 'None'}")

            if st.button(f"Use Template: {name}", key=f"gmail_use_template_{idx}"):
                st.session_state['selected_gmail_template'] = {
                    "name": name,
                    "subject": template['subject'],
                    "body": template['body'],
                    "attachment": template['attachment']
                }
                st.success(f"Template '{name}' loaded into form!")
            st.write("---")
    else:
        st.info("No templates available.")

    st.subheader("Delete a Gmail Template")
    if st.session_state['gmail_templates']:
        template_to_delete = st.selectbox("Select a template to delete", list(st.session_state['gmail_templates'].keys()))
        if st.button("Delete Template"):
            del st.session_state['gmail_templates'][template_to_delete]
            st.success(f"Template '{template_to_delete}' deleted successfully!")
