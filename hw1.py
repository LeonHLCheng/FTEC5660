#!/usr/bin/env python3
"""FTEC5660 HW1 student starter: build a chain for supermarket receipts."""

from __future__ import annotations

import argparse
import base64
import csv
import json
import mimetypes
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any


QUERY_1 = "How much money did I spend in total for these bills?"
QUERY_2 = "How much would I have had to pay without the discount?"
QUERIES = (QUERY_1, QUERY_2)
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
DUMMY_RESPONSE = "please design your chain to answer these two queries."


def load_env_file(path: Path = Path(".env")) -> None:
    """Load the simple KEY=VALUE entries used by this homework."""
    if not path.is_file():
        return
    import os

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def image_files(folder: Path) -> list[Path]:
    """Return supported images directly inside *folder*, sorted by filename."""
    return sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def image_data_url(path: Path) -> str:
    """Encode a local image in the format accepted by a multimodal prompt."""
    mime_type, _ = mimetypes.guess_type(path.name)
    mime_type = mime_type or "image/jpeg"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def build_chain() -> Any:
    """Create and return your LangChain chain once.

    Suggested imports:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_deepseek import ChatDeepSeek

    Use the vision-capable DeepSeek Flash model named
    ``deepseek-v4-flash-vision-exp``. The API key is loaded from .env.
    """
    ### YOUR CODE HERE
    import os
    from langchain_deepseek import ChatDeepSeek
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
    from langchain_core.runnables import RunnableLambda, RunnablePassthrough
    
    
    # Retrieve the API key from environment variables
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable is not set.")
    
    llm = ChatDeepSeek(
        model="deepseek-v4-flash-vision-exp",
        api_key=api_key,
        temperature=0.2, ##https://api-docs.deepseek.com/quick_start/parameter_settings/
        extra_body={"thinking": {"type": "disabled"}},   # one pass, no hidden reasoning
    )
    
    
    prompt_extract = ChatPromptTemplate.from_messages([
    (
        "human",
        [
            {"type": "text", "text": """
                 Extract all line items,
                 description,
                 amounts(Positive Sign amount of the item), 
                 discounts (negative sign amount of the item after the positive amount), 
                 subtotal, 
                 rounding(negative number between subtotal and final payments), 
                 final payment from this receipt image."""},
            {"type": "image_url", "image_url": {"url": "{encoded_image}"}},
        ],
    )
    ])
    
    prompt_transform = ChatPromptTemplate.from_template(
    """Transform the receipts items into a JSON object. Schema
    {{
        "items": [{{"amount": "float","description": "str","discount": "float"}}],
        "global_discounts": float,
        "rounding": float,
        "final_amount": float
    }}
    as keys:\n\n{receipt__details}"""
    )
    extraction_chain = prompt_extract | llm | StrOutputParser()
    full_chain = (
        {"receipt__details": extraction_chain}
        | prompt_transform
        | llm
        | StrOutputParser()
    )
    
        
    return full_chain


def answer_queries(chain: Any, images: list[Path]) -> dict[str, Any]:
    """Run your chain and return one response for each exact query string.

    ``images`` contains every receipt in the selected folder. A valid return
    value looks like:

        {QUERY_1: "HK$123.40", QUERY_2: "HK$150.00"}

    Use the provided ``image_data_url(path)`` helper to put local images in
    multimodal human messages. LangChain's ``batch`` method is one simple way
    to process independent receipt-extraction prompts in parallel.
    """
    ### YOUR CODE HERE
    
    #Result Parameter
    total_paid=0
    total_cost_without_discount=0
    
    for photo_path in images:
        print("Working on "+str(photo_path))
        #Encode_photo for sending
        AI_extracted_receipt = chain.invoke({"encoded_image": image_data_url(photo_path)})

        # Cleanup unwanted characters from the JSON passed by AI     
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", AI_extracted_receipt, re.DOTALL)
        if match:
            cleaned = match.group(1).strip()

        # Convert JSON string to Python dictionary       
        receipt = json.loads(cleaned)
        #print (receipt)
        
        #Recipt Level Statistic 
        total_amount = 0.0
        total_discount = 0.0
        
        
        for item in receipt["items"]:
            total_amount += item.get("amount", 0.0)
            total_discount += item.get("discount", 0.0)

        ''' #testing script
        grand_total_discount = (
            round(total_discount,2) + #item level Total Discount 
            round(receipt.get("global_discounts", 0.0),2) + #Global Discount
            round(receipt.get("rounding", 0.0),2)) # Rounding Discount
        
        print("Total item level amount:", round(total_amount,2))
        print("Total item level discount:", round(total_discount,2))
        print("Grand total discount (items + global):", round(grand_total_discount,2))
        print("AI Extracted Original Final Payement Amount : "+str(round(float(receipt.get("final_amount", 0.0)),2)))
        
        if(grand_total_discount<0):
            print("Calculated Based on AI Extraction Result : " + str(round(total_amount+grand_total_discount,2)))
            if round(total_amount+grand_total_discount,2) != round(float(receipt.get("final_amount", 0.0)),2):
                print('Error found in '+str(photo_path)+' AI Extraction')
        else:
            print("Calculated Based on AI Extraction Result : " + str(round(total_amount-grand_total_discount,2)))
            if round(total_amount-grand_total_discount,2) != round(float(receipt.get("final_amount", 0.0)),2):
                print('Error found in '+str(photo_path)+' AI Extraction')
        '''
        print('-------------------------------------------------------------------------')
        print()
        
        
        ##accumulate for final result
        total_paid +=receipt.get("final_amount", 0.0)
        total_cost_without_discount+=total_amount
        

    return {QUERY_1: round(total_paid,2), QUERY_2: round(total_cost_without_discount,2)}


# Everything below is provided runner/scoring code. No edits are needed.

_MONEY_RE = re.compile(
    r"(?<![\w.])(?:HK\$|\$)?\s*(-?\d[\d,]*(?:\.\d+)?)(?![\w.])",
    re.IGNORECASE,
)


def response_text(value: Any) -> str:
    """Convert common LangChain response shapes to text for results.csv."""
    content = getattr(value, "content", value)
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
        return "\n".join(parts).strip()
    if isinstance(content, (dict, list)):
        return json.dumps(content, ensure_ascii=False)
    return str(content).strip()


def parse_single_amount(text: str) -> Decimal | None:
    """Accept a response only when it contains exactly one numeric amount."""
    matches = _MONEY_RE.findall(text)
    if len(matches) != 1:
        return None
    try:
        return Decimal(matches[0].replace(",", "")).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None


def read_ground_truth(folder: Path) -> dict[str, Decimal]:
    """Read aggregate answers from the test folder."""
    path = folder / "ground_truth.json"
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    answers = data.get("answers", data)
    return {query: Decimal(str(answers[query])).quantize(Decimal("0.01")) for query in QUERIES}


def correctness_text(response: str, expected: Decimal | None) -> str:
    """Return `correct`, or an expected/predicted mismatch explanation."""
    if expected is None:
        return "not graded: ground_truth.json is missing"
    predicted = parse_single_amount(response)
    if predicted == expected:
        return "correct"
    shown = f"HK${predicted:.2f}" if predicted is not None else repr(response)
    return f"incorrect: expected HK${expected:.2f}, predicted {shown}"


def write_results(responses: dict[str, Any], truth: dict[str, Decimal]) -> Path:
    """Write the required three-column results.csv file."""
    output = Path("results.csv")
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["query", "model_response", "correctness"])
        for query in QUERIES:
            text = response_text(responses.get(query, "<missing response>"))
            writer.writerow([query, text, correctness_text(text, truth.get(query))])
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run FTEC5660 HW1 on receipt images")
    parser.add_argument(
        "--image-folder",
        required=True,
        type=Path,
        help="folder containing supermarket receipt images",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.image_folder.is_dir():
        raise SystemExit(f"not a folder: {args.image_folder}")

    images = image_files(args.image_folder)
    if not images:
        raise SystemExit(f"no supported images found in {args.image_folder}")

    load_env_file()
    chain = build_chain()
    responses = answer_queries(chain, images)
    if not isinstance(responses, dict):
        raise TypeError("answer_queries() must return a dictionary")

    output = write_results(responses, read_ground_truth(args.image_folder))
    print(f"Processed {len(images)} receipt(s). Wrote {output}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
