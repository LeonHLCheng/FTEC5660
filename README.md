# FTEC5660 Homework 1: Receipt Chain

Build a LangChain pipeline that reads every supermarket receipt in a folder
with the vision-capable DeepSeek Flash model and answers these two questions:

1. How much money did I spend in total for these bills?
2. How much would I have had to pay without the discount?

For this homework, **amount spent** means the final payment after the receipt's
rounding line. **Without the discount** means the sum of the original positive
item prices: add back every promotion, coupon, member, app, packaging-damage,
and percentage discount, but do not add back rounding.

## Student task

Only edit the two functions in `hw1.py` that contain `### YOUR CODE HERE`:

- `build_chain()` creates your LangChain chain.
- `answer_queries()` runs the chain on the receipt images and returns one final
  response for each question.

You may use prompt chaining, routing, parallel calls, reflection, or a
combination. Your final responses should each contain one HKD amount. Do not
hard-code filenames or public answers; grading uses unseen receipt folders.

## Setup and public test

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Put your DeepSeek key after `DEEPSEEK_API_KEY=` in `.env`, then run:

```bash
python3 hw1.py --image-folder public_test
```

The program creates `results.csv` in the current directory. Its columns are
`query`, `model_response`, and `correctness`. The public answers are in
`public_test/ground_truth.json`. The starter intentionally returns the dummy
response `please design your chain to answer these two queries.` so it runs
before you add any API code.

The required model is `deepseek-v4-flash-vision-exp`, the vision-capable
DeepSeek Flash model. JPEG, PNG, GIF, and WebP inputs are accepted by the
homework runner.


## Homework 1 solution: 
> to students: please fill your solution description here.

Visualization of the chain design


```
    ┌──────────────────────────────┐
    │           PC Folder          │
    │        - Image Files         │
    └───────────────┬──────────────┘
                    │
                    ▼
┌────────────────────────────────────────┐
│              Python Program            │
├────────────────────────────────────────┤
│ 1. Scan folder for images              │
│    - Identify all files inside the     │
│      target directory and filter       │
│      only those with image extensions  │
│                                        │
│ 2. Base64-encode each image            │
│    - Convert each image file into a    │
│      Base64 data URL                   │
│                                        │
│ 3. Build prompt chain                  │
│    - Stage 1: extract                  │
│    - Stage 2: transform JSON           │
│                                        │
│ 4. Send Base64 + prompts               │
│    - Invoke DeepSeek chain             │
└───────────────────┬────────────────────┘
                    │
                    ▼
  ┌──────────────────────────────────┐
  │          DeepSeek LLM            │
  ├──────────────────────────────────┤
  │ 5. LLM Step 1 — prompt_extract   │
  │    DeepSeek Vision interprets the│
  │    receipt image and extracts:   │
  │    - description                 │
  │    - amount                      │
  │    - discount                    │
  │    - subtotal                    │
  │    - rounding                    │
  │    - final payment               │
  │                                  │
  │ 6. Raw text output               │
  │    Receive unstructured text     │
  │    containing the extracted      │
  │    receipt information.          │
  │                                  │
  │ 7. LLM Step 2 — prompt_transform │
  │    - Convert to strict JSON      │
  │                                  │
  │ 8. Structured JSON output        │
  └─────────────────┬────────────────┘
                    │
                    ▼
    ┌──────────────────────────────┐
    │     Python Program (cont.)   │
    ├──────────────────────────────┤
    │ 9. Organize the data         │
    │    - item totals             │
    │    - discounts               │
    │    - rounding                │
    │    - final payment           │
    │                              │
    │ 10. Accumulate results       │
    │     - total paid             │
    │     - total cost w/o discount│
    │                              │
    │ 11. Output summarized CSV    │
    └───────────────┬──────────────┘
                    │
                    ▼    
    ┌──────────────────────────────┐
    │           PC Folder          │
    │      	- Result.CSV		       │
    └──────────────────────────────┘
```

Describing the solution

The core challenge of HW1 is to analyze receipt images and extract structured financial information in order to compute both the actual amount paid and the hypothetical amount without discounts, and through research and testing we confirmed that neither traditional programming nor pure LLM approaches can solve this reliably on their own:  

- Conventional programming alone struggles with this task because it requires strong OCR capabilities and complex rule‑based parsing to correctly interpret item descriptions, amounts, discounts, subtotals, rounding, and final payments.
- Pure LLM approaches also fall short because language models has limitation in performing mathematic calculation
accurately 

Therefore, I have adopted the solution as follows
1. Each receipt image is first encoded into Base64, but instead of embedding the Base64 directly into the prompt, which causes the LLM to treat the encoded bytes as text and misinterpret Base64 image data cause hallucinations of the result, We explicitly separate the prompt into a text block and an `image_url` block so the model correctly interprets the image.
2. During development, we tested multi‑image prompts but found that DeepSeek Vision becomes unstable when processing many images at once due to the limited size of each prompt, given that we unsure the number of the images in the private test, so we design to processes receipts one by one for accuracy.
3. After the LLM extracts raw text, a second prompt transforms the text into a strict JSON schema. During the development, we found that even if we asked LLM to return the JSON format, there still have chances that LLM Return result cannot be directly use due to some special characters / additional text is provided during LLM return, therefore a logic is added in python to removing Markdown fences or stray characters before parsing. This structured JSON allows the program to compute item totals, item‑level discounts, global discounts, rounding adjustments, and final payments.
4. Because the LLM captures both item‑level and receipt‑level discount information, the program can easily extend to more complex analyses by writing additional python logic. For HW1, we simply sum each receipt’s final payment (after rounding) and compute how much would have been paid without discounts by summing the original item prices.
