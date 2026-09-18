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
    │      - summarized CSV        │
    └──────────────────────────────┘
\
