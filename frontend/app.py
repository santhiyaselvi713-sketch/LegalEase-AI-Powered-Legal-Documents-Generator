import base64
import html
import os

import requests
import streamlit as st

from dotenv import load_dotenv


load_dotenv()


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(

    page_title="LegalEase",

    page_icon="⚖️",

    layout="wide"
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {

        text-align: center;

        font-size: 45px;

        font-weight: 700;

        margin-bottom: 0;
    }

    .subtitle {

        text-align: center;

        color: #777;

        margin-bottom: 25px;
    }

    .legal-preview {

        background: #111827;

        color: #f9fafb;

        border-radius: 14px;

        padding: 30px;

        max-height: 650px;

        overflow-y: auto;

        line-height: 1.7;

        font-family:
            Georgia,
            "Times New Roman",
            serif;
    }

    .legal-preview h1 {

        color: white;

    }

    .legal-preview h2 {

        color: white;

    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">⚖️ LegalEase</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'AI-Powered Legal Document Generator'
    '</div>',
    unsafe_allow_html=True
)


st.warning(
    "LegalEase generates draft legal information, "
    "not legal advice. Review the final document "
    "before relying on it."
)


# --------------------------------------------------
# INPUT FORM
# --------------------------------------------------

with st.form("legal_document_form"):

    left, right = st.columns(2)

    with left:

        document_type = st.text_input(

            "Document Type",

            value="Freelance Work Contract",

            placeholder=(
                "Example: NDA"
            )
        )


        parties = st.text_area(

            "Parties Involved",

            value=(
                "Jane Doe "
                "(Service Provider), "
                "TechNova Inc. "
                "(Client)"
            ),

            height=120,

            placeholder=(
                "Example: "
                "Alice (Tenant), "
                "ABC Ltd (Landlord)"
            )
        )


        dates = st.text_input(

            "Effective Date",

            value="September 24, 2026"
        )


    with right:

        jurisdiction = st.text_input(

            "Jurisdiction",

            placeholder=(
                "Example: Tamil Nadu, India"
            )
        )


        language = st.selectbox(

            "Language",

            [
                "English",
                "Tamil",
                "Hindi"
            ]
        )


        terms = st.text_area(

            "Terms & Conditions",

            value=(
                "Payment to be made within "
                "30 days of invoice; "
                "The provider agrees to deliver "
                "work by the agreed deadline; "
                "Confidentiality must be maintained; "
                "Either party may terminate "
                "with 15 days notice"
            ),

            height=180,

            help=(
                "Separate terms using semicolons (;)."
            )
        )


    generate_button = st.form_submit_button(

        "✨ Generate Document",

        use_container_width=True
    )


# --------------------------------------------------
# GENERATE
# --------------------------------------------------

if generate_button:

    payload = {

        "document_type":
            document_type,

        "parties":
            parties,

        "terms":
            terms,

        "dates":
            dates,

        "jurisdiction":
            jurisdiction,

        "language":
            language
    }


    try:

        with st.spinner(
            "Generating legal document..."
        ):

            response = requests.post(

                f"{BACKEND_URL}/generate",

                json=payload,

                timeout=90
            )


        response.raise_for_status()


        result = response.json()


        st.session_state.document = (
            result["document"]
        )

        st.session_state.document_type = (
            document_type
        )

        st.session_state.ai_generated = (
            result["ai_generated"]
        )

        st.session_state.model = (
            result["model"]
        )


        if result["ai_generated"]:

            st.success(
                "Document generated successfully "
                "using Gemini AI."
            )

        else:

            st.info(
                "Gemini was not available, so "
                "LegalEase used the local fallback."
            )


    except requests.RequestException as error:

        st.error(
            f"Backend connection failed: {error}"
        )

        st.info(
            "Make sure FastAPI is running."
        )


# --------------------------------------------------
# DOCUMENT EDITOR
# --------------------------------------------------

if "document" in st.session_state:

    st.divider()

    st.subheader(
        "📄 Generated Document"
    )


    edited_document = st.text_area(

        "Edit your document",

        value=st.session_state.document,

        height=550,

        key="editable_document"
    )


    st.session_state.document = (
        edited_document
    )


    # --------------------------------------------------
    # PREVIEW
    # --------------------------------------------------

    st.subheader(
        "👁️ Preview"
    )


    safe_document = html.escape(
        edited_document
    )


    safe_document = (
        safe_document
        .replace(
            "\n\n",
            "</p><p>"
        )
        .replace(
            "\n",
            "<br>"
        )
    )


    st.markdown(

        f"""
        <div class="legal-preview">

        <p>
        {safe_document}
        </p>

        </div>
        """,

        unsafe_allow_html=True
    )


    # --------------------------------------------------
    # DOWNLOAD
    # --------------------------------------------------

    st.divider()

    st.subheader(
        "⬇️ Download Document"
    )


    col1, col2, col3 = st.columns(3)


    filename = "".join(

        character

        if character.isalnum()
        or character in "-_"

        else "_"

        for character
        in st.session_state.document_type.lower()
    )


    filename = (
        filename.strip("_")
        or "legalease_document"
    )


    # --------------------------------------------------
    # TXT
    # --------------------------------------------------

    with col1:

        st.download_button(

            label="⬇️ Download TXT",

            data=edited_document.encode(
                "utf-8"
            ),

            file_name=f"{filename}.txt",

            mime="text/plain",

            use_container_width=True
        )


    # --------------------------------------------------
    # DOCX
    # --------------------------------------------------

    with col2:

        if st.button(
            "Prepare DOCX",
            use_container_width=True
        ):

            st.session_state.docx_ready = True


        if st.session_state.get(
            "docx_ready",
            False
        ):

            try:

                from backend.services.document_formatter import (
                    format_docx
                )


                docx_data = format_docx(

                    edited_document,

                    st.session_state.document_type
                )


                st.download_button(

                    label="⬇️ Download DOCX",

                    data=docx_data,

                    file_name=f"{filename}.docx",

                    mime=(
                        "application/"
                        "vnd.openxmlformats-officedocument."
                        "wordprocessingml.document"
                    ),

                    use_container_width=True
                )


            except Exception as error:

                st.error(
                    f"DOCX export failed: {error}"
                )


    # --------------------------------------------------
    # PDF
    # --------------------------------------------------

    with col3:

        if st.button(
            "Prepare PDF",
            use_container_width=True
        ):

            st.session_state.pdf_ready = True


        if st.session_state.get(
            "pdf_ready",
            False
        ):

            try:

                from backend.services.document_formatter import (
                    format_pdf
                )


                pdf_data = format_pdf(

                    edited_document,

                    st.session_state.document_type
                )


                st.download_button(

                    label="⬇️ Download PDF",

                    data=pdf_data,

                    file_name=f"{filename}.pdf",

                    mime="application/pdf",

                    use_container_width=True
                )


            except Exception as error:

                st.error(
                    f"PDF export failed: {error}"
                )