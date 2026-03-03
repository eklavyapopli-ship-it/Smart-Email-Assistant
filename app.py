import streamlit as st
import requests
import time

BACKEND_URL = "http://localhost:8000"  

st.set_page_config(page_title="RAG Upload Dashboard", layout="centered")

st.title("📂 RAG File Processor")

uploaded_file = st.file_uploader("Upload a file", type=["pdf", "txt", "docx"])

if uploaded_file is not None:
    if st.button("Upload & Process"):
        
        with st.spinner("Uploading file..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            response = requests.post(f"{BACKEND_URL}/uploadfile/", files=files)

        if response.status_code == 200:
            data = response.json()
            job_id = data.get("job")

            st.success("File uploaded successfully!")
            st.write("🆔 Job ID:", job_id)

            st.info("Processing started...")

           
            progress_bar = st.progress(0)

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