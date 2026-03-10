# Interactive first — no parameters required

For **non-technical users**: run any script with **no arguments**. You will be asked what to do and for any text input. No need to remember commands or quote text on the command line.

## How to run (no parameters)

| Run this | What happens |
|----------|----------------|
| `python main.py` | Menu: Quick check, Full suite with my text, or Full suite (default). Then prompted for text if needed. |
| `python main.py --check` | Prompted for your text, then quick result. |
| `python main.py --user` | Prompted for your text, then full 10-step suite. |
| `python integration/run_complete.py` | Prompted for your text (or path to file), then pipeline runs. |
| `python integration/run_user_result.py` | Prompted for your text, then shows result only. |
| `python integration/structural_prediction_loop.py` | Prompted for your text, then runs prediction loop. |
| `python santek_sle.py` | Asked: use default corpus (Y/n)? Or enter your own text(s). |
| `threshold-onset` (no command) | Menu: Run pipeline, Quick check, Full suite, Validate, Benchmark, Help. |
| `threshold-onset run` | Prompted for text if you didn’t pass any. |
| `threshold-onset check` | Prompted for text if you didn’t pass any. |

## Multi-line text

When a script asks for text:

- Type or **paste** your text.
- Press **Enter twice** (empty line) when you are done.
- Or use **Ctrl+D** (Unix) / **Ctrl+Z** then Enter (Windows) to finish.

## Still use parameters if you want

You can still pass text and flags as before, e.g.:

- `python main.py --check "Your text here"`
- `python integration/run_complete.py --default`  (use built-in text, no prompt)
- `python integration/structural_prediction_loop.py --default`  (use default text)

Scripts that support `--default` use built-in sample text and do not prompt.

## Shared helper

All interactive prompts use `integration/interactive_prompt.py` so behaviour and wording are consistent across the project.
