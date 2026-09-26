from typing import Optional

from backend.config import get_settings


SYSTEM_INSTRUCTIONS = """
You are LegalEase, an AI legal-document drafting assistant.

Your task is to create a professional LEGAL DOCUMENT DRAFT
using only the information supplied by the user.

IMPORTANT RULES:

1. Do not invent names.
2. Do not invent dates.
3. Do not invent addresses.
4. Do not invent payment amounts.
5. Do not invent laws or statutes.
6. Do not invent case citations.
7. If information is missing, use:
   [MISSING INFORMATION]

8. Preserve the user's supplied terms.
9. Use professional and neutral legal language.
10. Organize the document using clear headings.
11. Include the parties.
12. Include the effective date.
13. Include relevant obligations.
14. Include relevant confidentiality provisions when appropriate.
15. Include termination provisions when appropriate.
16. Include governing-law information if supplied.
17. Include signature sections.
18. Clearly identify the result as a draft.
19. Never claim that the document has been reviewed by a lawyer.
20. Never claim that the document is guaranteed legally valid.
21. Never create a fake lawyer name, signature, or license number.

Return the complete document as plain text or Markdown.
"""


def create_fallback_document(
    document_type: str,
    parties: str,
    terms: str,
    dates: str,
    jurisdiction: str,
) -> str:

    term_items = [
        item.strip()
        for item in terms.split(";")
        if item.strip()
    ]

    terms_text = "\n".join(
        f"{index}. {term}"
        for index, term in enumerate(term_items, start=1)
    )

    jurisdiction_text = (
        jurisdiction
        if jurisdiction
        else "[GOVERNING LAW / JURISDICTION]"
    )

    return f"""
# {document_type.upper()}

**DRAFT — REVIEW REQUIRED**

This document is an informational draft generated from
the information supplied by the user.

It is not legal advice and has not been reviewed by a lawyer.

## 1. PARTIES

{parties}

## 2. EFFECTIVE DATE

{dates}

## 3. TERMS AND CONDITIONS

{terms_text}

## 4. TERM AND TERMINATION

The parties should confirm the applicable term and
termination conditions before signing this document.

## 5. GOVERNING LAW

{jurisdiction_text}

## 6. ENTIRE AGREEMENT

This draft should be reviewed for completeness,
accuracy and consistency before execution.

## 7. SIGNATURES

PARTY 1

Signature: ______________________________

Name: __________________________________

Date: ___________________________________


PARTY 2

Signature: ______________________________

Name: __________________________________

Date: ___________________________________
"""


class GeminiDocumentGenerator:

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):

        settings = get_settings()

        self.api_key = (
            api_key
            if api_key
            else settings.gemini_api_key
        )

        self.model = (
            model
            if model
            else settings.gemini_model
        )

        self.client = None

        if self.api_key:

            try:

                from google import genai

                self.client = genai.Client(
                    api_key=self.api_key
                )

            except Exception:

                self.client = None

    def generate_document(
        self,
        document_type: str,
        parties: str,
        terms: str,
        dates: str,
        jurisdiction: str = "",
        language: str = "English"
    ):

        # If Gemini API isn't configured,
        # use a deterministic local fallback.

        if not self.client:

            document = create_fallback_document(
                document_type,
                parties,
                terms,
                dates,
                jurisdiction
            )

            return document, False

        prompt = f"""
{SYSTEM_INSTRUCTIONS}

LANGUAGE:
{language}

DOCUMENT TYPE:
{document_type}

PARTIES:
{parties}

EFFECTIVE DATE:
{dates}

JURISDICTION:
{jurisdiction if jurisdiction else "[NOT PROVIDED]"}

TERMS AND CONDITIONS:
{terms}

Generate the complete legal document draft now.
"""

        try:

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            generated_text = getattr(
                response,
                "text",
                None
            )

            if not generated_text:

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return generated_text.strip(), True

        except Exception as error:

            fallback = create_fallback_document(
                document_type,
                parties,
                terms,
                dates,
                jurisdiction
            )

            fallback += (
                "\n\n"
                "[AI service fallback activated: "
                f"{type(error).__name__}]"
            )

            return fallback, False