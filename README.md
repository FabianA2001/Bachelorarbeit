# Degree-Constrained Triangulations

| Category    | Details         |
| ----------- | --------------- |
| Supervisors | Dr. Phillip Keldenich    |
|             | Michael Perk    |
| Student     | Fabian Alich      |
| Student ID  | xxxxxxx        |
| Email       |  |
| Title       | xxxxxxx       |
| Deadline    | 2025-04-22      |

You can find a reference repository [here](https://gitlab.ibr.cs.tu-bs.de/alg/example_student_thesis_algorithm_engineering).

## Task Description

TODO!

## Common Pitfalls

Here are some common pitfalls that you should avoid:

### Organization

- Regularly synchronize with your supervisors to clarify expectations and avoid
  misunderstandings. They are available to assist, so always feel free to ask
  questions.
- Commit your changes to the repository consistently to safeguard your work and
  keep your supervisors updated on your progress.
- Communicate openly with your supervisors about any lack of progress. They can
  provide guidance and support to help you overcome obstacles.
- Begin drafting your thesis early to ensure there is ample time for revisions
  and feedback. Providing drafts for commentary can significantly enhance the
  support you receive from your supervisors.
- Document the outcomes and decisions of meetings with your supervisors in
  meeting minutes. Store these minutes in
  [materials/meetings](./materials/meetings) for easy reference by both you and
  your supervisors.
- Take personal responsibility for tracking deadlines. Communicate proactively
  if you anticipate difficulties in meeting them.
- Maintain regular communication with your supervisors; do not wait for them to
  initiate contact. They manage multiple responsibilities and students, which
  can skew their perception of time. Ensuring they are informed of your progress
  is your responsibility.

### Content

- Avoid first-person pronouns; use the impersonal "we" to engage the reader.
- Eliminate contractions; write "do not" instead of "don't."
- Refrain from using slang or colloquial expressions; maintain a formal tone.
- Ensure every sentence is purposeful and supported by evidence. Avoid filler
  statements such as "The Traveling Salesman Problem has fascinated researchers
  for decades" unless further explanation is provided.
- Define all terms clearly and use them consistently.
- Avoid superlatives and unsubstantiated claims. Support all assertions with
  evidence.
- Keep sentences and paragraphs concise. Limit sentences to one or two ideas,
  and paragraphs to a few cohesive points.
- Use visuals like figures and tables to complement your text, and ensure they
  are well-explained within your narrative.
- Introduce each section with a brief paragraph to outline its content.
- Keep captions concise but informative, allowing figures and tables to be
  understood independently.

You can get more useful hints in
[How to write a Master Thesis](https://users.aalto.fi/~jsaramak/HowToWriteMastersThesis.pdf).

### LaTeX

- Use an empty line instead of `\\` for new paragraphs for better readability.
- Prefer `\[` and `\]` over `$$` for creating math environments.
- Keep LaTeX code lines short and break them after a sentence or a comma for
  easier version control and better error messages.
- Position figures at the top or bottom of pages using `[tb]` to enhance
  document layout.
- Utilize the `cleveref` package for smart referencing and the `siunitx` package
  for consistent unit and number formatting.
- Use `booktabs` for professional table formatting and `hyperref` for navigable
  document links.
- Employ `todonotes` for inline comments and reminders.
- Add a `~` before `\cite` to tell LaTeX that the `et al.` is not the end of a
  sentence.
- Use vector graphics for figures to ensure high-quality rendering at any scale.
  Only use raster graphics when necessary.

You can find a basic introduction into professional LaTeX writing in
[LaTeX in 30min](https://www.overleaf.com/learn/latex/Learn_LaTeX_in_30_minutes).

### Python

- Ensure you use `__init__.py` in directories to treat them as packages.
- Package your code for installation via `pip` and ensure it is well-organized.
- Implement type hints to clarify and enhance code usability.
- Protect the main script block with `if __name__ == "__main__":` to prevent
  execution during module import.
- Familiarize yourself with list, dictionary, and set comprehensions for
  efficient coding.
- Leverage the `itertools` module for advanced iterable manipulations.
- Use `pathlib` for reliable path management across different operating systems.
- Replace `print` statements with `logging` for better control over debugging
  and output.
- Avoid mutable default arguments in function definitions to prevent unexpected
  behavior.
- Document dependencies clearly in `requirements.txt` or `setup.py` for
  reproducibility.
- Use virtual environments to manage dependencies and isolate project
  environments. Test your code in a clean environment before handing it in.

[Scientific Coding in Python](https://learn.scientific-python.org/development/)
gives you a lot of useful hints for creating high-quality Python projects for
scientific purposes.

### C++

- Provide clear documentation, including a `README.md`, for building and running
  C++ code, especially when standard build systems are not used.

### Empirical Evaluation

- Adhere to the guidelines outlined in the
  [SIGPLAN Checklist for empirical evaluation](https://raw.githubusercontent.com/SIGPLAN/empirical-evaluation/master/checklist/checklist.pdf)
  to ensure your empirical work meets established standards.
- Record comprehensive details of your experiments, such as random seeds, code
  versions, and library versions, to enable exact replication.
- Rigorously verify your evaluation code to confirm its correctness and
  functionality. Undetected bugs can compromise the validity of your results and
  may be construed as scientific misconduct.
- Carefully consider how to present your findings. Provide specific data points,
  summary statistics, and visual aids to enhance the accessibility and
  comprehensibility of your results.
- Conduct exploratory experiments to familiarize yourself with the data and
  adjust your evaluation strategy as needed. This proactive approach can help
  identify and address potential issues early on.
- Clearly define the objectives of each experiment before beginning. Detail the
  design of the experiment and how it addresses specific research questions.
  Analyze the results with these questions in mind to avoid practices like
  p-hacking. Discuss the limitations of your evaluation and strategies employed
  to mitigate potential threats to validity.
- Prepare for the possibility of discovering significant flaws during the
  evaluation phase. Allocate sufficient time to address these issues. Prioritize
  conducting a thorough, accurate evaluation over a more extensive but
  potentially flawed one.

## Structure of the Repository

- `README.md`: This file should give a general overview of the project.
- `.gitignore`: This file is already prepared to ignore common artifacts of
  LaTeX and Python.
- `.pre-commit-config.yaml`: A configuration to run various tools and checks
  automatically for Python and other files.
- `code/`: This directory should contain the implemented algorithms.
- `thesis/`: This directory should contain the written thesis.
- `evaluation/`: This directory should contain the empirical evaluation.
- `materials/`: This directory should contain any additional materials that are
  relevant for the project.

## Useful Tools

- [pre-commit](https://pre-commit.com/): A framework for managing and
  maintaining multi-language pre-commit hooks. Use `pre-commit run --all-files`
  to run in on all files. You can install pre-commit with
  `pip install pre-commit`. Use it frequently to keep you code clean and detect
  problems early.
- [CheckMyTex](https://github.com/d-krupke/CheckMyTex): Is a tool developed by
  us that wraps around a bunch of other tools to check your LaTeX code for
  common mistakes. It is relatively easy to set up on Mac and Linux, but does
  not support Windows. You can also use the tools it wraps around directly, but
  this is more cumbersome and requires you to filter out many more false
  positives.

