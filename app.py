import streamlit as st
import requests
import time

BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="RAG + Email Agent Dashboard", layout="wide")

st.title("Context Aware Email Agent")


left_col, right_col = st.columns(2)


with left_col:
    with st.container():
        st.header("Upload File for RAG")

        uploaded_file = st.file_uploader(
            "Upload a file",
            type=["pdf", "txt", "docx"]
        )

        if uploaded_file is not None:
            if st.button("Upload & Process"):

                with st.spinner("Uploading file..."):
                    files = {
                        "file": (uploaded_file.name, uploaded_file.getvalue())
                    }
                    response = requests.post(
                        f"{BACKEND_URL}/uploadfile/",
                        files=files
                    )

                if response.status_code == 200:
                    data = response.json()
                    job_id = data.get("job")

                    st.success("File uploaded successfully!")
                    st.write("🆔 Job ID:", job_id)

                    progress_bar = st.progress(0)
                    st.info("Processing started...")

                    for i in range(100):
                        time.sleep(1)

                        status_response = requests.get(
                            f"{BACKEND_URL}/job-status",
                            params={"job_id": job_id}
                        )

                        result_data = status_response.json()

                        if result_data.get("result") is not None:
                            progress_bar.progress(100)
                            st.success("Processing Complete 🎉")
                            st.write("### Result:")
                            st.write(result_data["result"])
                            break

                        progress_bar.progress(i + 1)
                    else:
                        st.warning("Still processing... Try refreshing later.")

                else:
                    st.error("Upload failed!")


with right_col:
    with st.container():
        st.header("Email Agent Chat")
        
        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        
        # Display chat history
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input

        user_input = st.text_area("Ask Email Agent...", key="chat_input", height=80)
        send = st.button("Send", use_container_width=True)

        if send and user_input:

            
            st.session_state.chat_history.append(
                {"role": "user", "content": user_input}
            )
            with st.chat_message("user"):
                st.markdown(user_input)

            
            response = requests.post(
                f"{BACKEND_URL}/chat",
                params={"query": user_input}
            )

            if response.status_code == 200:
                job_id = response.json().get("job")

                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    message_placeholder.markdown("Processing...")

                    
                    while True:
                        time.sleep(2)

                        status_response = requests.get(
                            f"{BACKEND_URL}/chat-job-status",
                            params={"job_id": job_id}
                        )

                        result_data = status_response.json()
                        result = result_data.get("result")

                        if result is not None:
                            message_placeholder.markdown(result)

                            st.session_state.chat_history.append(
                                {"role": "assistant", "content": result}
                            )
                            break
            else:
                st.error("Failed to start email job.")