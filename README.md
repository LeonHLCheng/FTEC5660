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

The core challenge of HW1 is to analyze receipt images and extract structured financial information in order to compute both the actual amount paid and the hypothetical amount without discounts, and through research and testing it is confirmed that neither traditional programming nor pure LLM approaches can solve this reliably on their own:  

- Conventional programming alone struggles with this task because it requires strong OCR capabilities and complex rule‑based parsing to correctly interpret item descriptions, amounts, discounts, subtotals, rounding, and final payments.
- Pure LLM approaches also fall short because language models has limitation in performing mathematic calculation
accurately 

Therefore, I have adopted the solution as follows
1. Each receipt image is first encoded into Base64, but instead of embedding the Base64 directly into the prompt, which causes the LLM to treat the encoded bytes as text and misinterpret Base64 image data cause hallucinations of the result, I explicitly separate the prompt into a text block and an `image_url` block so the model correctly interprets the image.
2. During development, I tested multi‑image prompts but found that DeepSeek Vision becomes unstable when processing many images at once due to the limited size of each prompt, given that it is unsure the number of the images in the private data test, so it is designed to processes receipts one by one for accuracy.
3. After the LLM extracts raw text, a second prompt transforms the text into a strict JSON schema. During the development, I found that even if asked LLM to return the JSON format, there still have chances that LLM Return result cannot be directly use due to some special characters / additional text is provided during LLM return, therefore a logic is added in python to removing Markdown fences or stray characters before parsing. This structured JSON allows the program to compute item totals, item‑level discounts, global discounts, rounding adjustments, and final payments.
4. Because my solution already captures both item‑level and receipt‑level discount information, the program can easily extend to more complex analyses by writing additional python logic. For HW1, just simply sum each receipt’s final payment (after rounding) and compute how much would have been paid without discounts by summing the original item prices.


##Reflection

During the past ten days, I felt as if the world had tilted slightly faster than usual. Every morning brought another headline about a new breakthrough in artificial intelligence. GPT 6 appeared with abilities that felt almost unreal. Google announced progress in simulating the brain of a fruit fly, hinting at a future where biological intelligence and machine intelligence might begin to overlap.

These events did not feel distant. They felt personal, almost like someone had reached into my memories and accelerated them.

I kept thinking back to my undergraduate final year. Six years ago, I was sitting in a small computer lab, training a transformer model to understand text. At that time, the idea of teaching a machine to read felt magical. My classmates and I celebrated when our model outperformed rule‑based chatbots. We believed we were touching the frontier. Yet even then, I remember staring at the loss curves and wondering how the model truly made its decisions. The black box felt mysterious, and I carried that doubt quietly.

Now, that same doubt has grown into something larger. GPT 6 does not simply read text. It creates three‑dimensional objects, builds game logic, and orchestrates complex tasks. It feels like the black box has expanded into a black universe. I am excited by the possibilities, but I also feel a pressure that sits behind my ribs. The pace is breathtaking, and I worry about how to keep up.

In my short career as a FinTech consultant, clients often ask how to adopt artificial intelligence. Their questions are practical. They want help with repetitive tasks or faster ways to consolidate information. I try to guide them, but the gap between what industry expects and what frontier AI can already do is widening. When I read about GPT 6 creating entire interactive worlds, I realise that my current understanding is not enough. I need to grow, not only in technical skill but in the ability to translate advanced AI into real‑world solutions.

My recent attempts to use agentic systems such as Antigravity made this gap even clearer. I asked the system to perform tasks, but the results often drifted away from what I expected. It felt like trying to steer a boat that responded to the wind more than the rudder. I became frustrated, not because the AI was wrong, but because I did not yet know how to guide it. That frustration slowly turned into motivation. I realised that the future challenge is not simply learning how to use AI. The challenge is learning how to direct it, shape it, and collaborate with it.

This is why I wanted to join this course. I want to understand the deeper principles behind these systems. I want to learn how to control them, how to evaluate them, and how to apply them responsibly. I want to build solutions that matter, solutions that help society rather than overwhelm it.

At the same time, I cannot ignore a quieter fear. When I read about biological simulations of animal brains, I wonder what the future will look like when machines begin to think in ways that resemble living creatures. I wonder what skills humans will need when artificial intelligence becomes not only capable, but possibly self‑directed. I wonder how I should prepare myself for a world where intelligence is no longer limited to biology.

These ten days did not simply inform me. They changed my direction. They reminded me that the world is entering a new chapter, and I want to be someone who understands it rather than someone who is swept away by it. I want to learn how to work with AI, how to guide it, and how to build a future where human creativity and machine capability can coexist with purpose.
